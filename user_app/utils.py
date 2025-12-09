import re
import secrets

from django.contrib.auth import password_validation
from config import settings
from user_app.models import User
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

USERNAME_MIN_LENGTH = 5


def validate_username(username):
    if User.objects.filter(username=username).exists():
        return {
            "success": False,
            "reason": _("Bu foydalanuvchi nomi mavjud!"),
        }

    if len(username.replace("/", "")) < USERNAME_MIN_LENGTH:
        return {
            "success": False,
            "reason": _(f"Foydalanuvchi nomingiz {USERNAME_MIN_LENGTH} ta belgidan kam bo'lmasligi kerak!"),
        }

    if not username.isalnum():
        return {
            "success": False,
            "reason": _("Matriculation number should be alphanumeric"),
        }

    return {
        "success": True,
    }


def validate_email(email):
    if User.objects.filter(email=email).exists():
        return {"success": False, "reason": _(f"Bu E-mail mavjud!")}
    if not re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email):
        return {"success": False, "reason": _("E-mail talabga javob bermaydi!")}
    if email is None:
        return {"success": False, "reason": _("E-mailingizni kiriting!")}
    return {"success": True}


def send_message_email(template, data, to_email, subject):
    try:
        htmly = get_template(template)
        html_content = htmly.render(data)
        message = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, [to_email])
        message.attach_alternative(html_content, "text/html")
        message.send()
    except Exception as e:
        print("Pochtaga ma'lumot yuborilmadi")
        print(f"{e}")


def clean_password1(password1):
    password_validation.validate_password(password1)


def generate_token():
    return secrets.token_hex(16)
