import json

import requests
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from online_users.models import OnlineUserActivity

from admin1.models import Admin1
from article_app.models import *
from django.contrib.auth import logout, authenticate, login, update_session_auth_hash

from moderator.models import Moderator
from pupil.models import Pupil
from test_maker.models import LanguageTest, Subject, Teacher
from expert.models import Expert
from fileapp.models import TemplateFile
from journal.models import Journal
from user_app.decorators import unauthenticated_user, allowed_users, orientation_user
from django.db.models.query_utils import Q
from user_app.forms import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from user_app.models import User, ReviewerArticle, StatusReview
from user_app.utils import *
import numpy as np
from django.template.loader import render_to_string, get_template
from django.utils.translation import activate, get_language
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.core.paginator import Paginator
from captcha.models import CaptchaStore


def logout_user(request):
    logout(request)
    response = redirect('main_page')
    response.delete_cookie('page')
    return response


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def home(request):
    user = get_object_or_404(User, pk=request.user.id)
    user_status = OnlineUserActivity.get_user_activities(timedelta(seconds=5))

    count_published_articles = Article.objects.all().filter(is_publish=True, is_publish_journal=True).count()
    count_published_journals = Journal.objects.all().filter(status=True, is_publish=True).count()
    count_ready_publish_articles = Article.objects.all().filter(is_publish=True, is_publish_journal=False).count()
    count_reviewing_articles = Article.objects.all().exclude(article_status_id=2).exclude(article_status_id=3).exclude(
        article_status_id=6).exclude(article_status_id=9).count()
    total_users = User.objects.all().count()
    total_editors = Editor.objects.all().filter(is_editor=True).count()
    total_reviewers = Reviewer.objects.all().filter(is_reviewer=True).count()
    total_request_reviewers = Reviewer.objects.all().filter(is_reviewer=False).count()
    total_admins = User.objects.all().filter(roles__code_name='admin').count()
    total_online_users = user_status.count()

    context = {
        'count_published_articles': count_published_articles,
        'count_published_journals': count_published_journals,
        'count_ready_publish_articles': count_ready_publish_articles,
        'count_reviewing_articles': count_reviewing_articles,
        'total_users': total_users,
        'total_editors': total_editors,
        'total_reviewers': total_reviewers,
        'total_request_reviewers': total_request_reviewers,
        'total_admins': total_admins,
        'total_online_users': total_online_users,
        'user': user,
    }
    return render(request, "user_app/settings/home.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def countries_list(request):
    objects = Country.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/country.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_country(request):
    if request.method == "POST":
        form = CreateCountryForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateCountryForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_country.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_country(request, pk):
    country = get_object_or_404(Country, pk=pk)
    if request.method == "POST":
        form = CreateCountryForm(request.POST, instance=country)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateCountryForm(instance=country)
        context = {
            'form': form,
            'country': country,
        }
        return render(request, "user_app/crud/edit_country.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_country(request, pk):
    country = get_object_or_404(Country, pk=pk)
    if request.method == "POST":
        country.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'country': country,
        }
        return render(request, "user_app/crud/delete_country.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def editors_list(request):
    objects = Editor.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/editors.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def regions_list(request):
    objects = Region.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/region.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_region(request):
    if request.method == "POST":
        form = CreateRegionForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateRegionForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_region.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_region(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == "POST":
        form = CreateRegionForm(request.POST, instance=region)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateCountryForm(instance=region)
        context = {
            'form': form,
            'region': region,
        }
        return render(request, "user_app/crud/edit_region.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_region(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == "POST":
        region.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'region': region,
        }
        return render(request, "user_app/crud/delete_region.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def genders_list(request):
    objects = Gender.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/genders.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_gender(request):
    if request.method == "POST":
        form = CreateGenderForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateGenderForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_gender.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_gender(request, pk):
    gender = get_object_or_404(Gender, pk=pk)
    if request.method == "POST":
        form = CreateGenderForm(request.POST, instance=gender)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateGenderForm(instance=gender)
        context = {
            'form': form,
            'gender': gender,
        }
        return render(request, "user_app/crud/edit_gender.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_gender(request, pk):
    gender = get_object_or_404(Gender, pk=pk)
    if request.method == "POST":
        gender.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'gender': gender,
        }
        return render(request, "user_app/crud/delete_gender.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def menus_list(request):
    objects = Menu.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/menus.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_menu(request):
    if request.method == "POST":
        form = CreateMenuForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateMenuForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_menu.html", context=context)


@login_required(login_url='login')
# @allowed_users(role=['admin', 'editor'])
def edit_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == "POST":
        form = CreateMenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateMenuForm(instance=menu)
        context = {
            'form': form,
            'menu': menu,
        }
        return render(request, "user_app/crud/edit_menu.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == "POST":
        menu.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'menu': menu,
        }
        return render(request, "user_app/crud/delete_menu.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def roles_list(request):
    objects = Role.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/roles.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_role(request):
    if request.method == "POST":
        form = CreateRoleForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateRoleForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_role.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == "POST":
        form = CreateRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateRoleForm(instance=role)
        context = {
            'form': form,
            'role': role,
        }
        return render(request, "user_app/crud/edit_role.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == "POST":
        role.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'role': role,
        }
        return render(request, "user_app/crud/delete_role.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def scientific_degrees_list(request):
    objects = ScientificDegree.objects.all()
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/scientific_degrees.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_scientific_degree(request):
    if request.method == "POST":
        form = CreateScientificDegreeForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli yaratildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateScientificDegreeForm()
        context = {
            'form': form,
        }
        return render(request, "user_app/crud/create_scientific_degree.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_scientific_degree(request, pk):
    degree = get_object_or_404(ScientificDegree, pk=pk)
    if request.method == "POST":
        form = CreateScientificDegreeForm(request.POST, instance=degree)
        if form.is_valid():
            form.save()
            data = {
                "message": _("Muvaffaqiyatli o'zgartirildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "message": _("Ma'lumot to'liq emas!")
            }
            return JsonResponse(data)
    else:
        form = CreateRoleForm(instance=degree)
        context = {
            'form': form,
            'degree': degree,
        }
        return render(request, "user_app/crud/edit_scientific_degree.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_scientific_degree(request, pk):
    degree = get_object_or_404(ScientificDegree, pk=pk)
    if request.method == "POST":
        degree.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'degree': degree,
        }
        return render(request, "user_app/crud/delete_scientific_degree.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def users_list(request):
    objects = User.objects.all().order_by('-id')
    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_count = page_obj.paginator.page_range
    p_n = paginator.count
    context = {
        'page_obj': page_obj,
        'page_count': page_count,
        'p_n': p_n,
    }
    return render(request, "user_app/settings/users.html", context=context)


@login_required(login_url='login')
def load_menus(request):
    user = get_object_or_404(User, id=request.user.id)
    menus0 = Menu.objects.filter(status=True).filter(type=0).filter(system_type=0).order_by('order')
    menus1 = Menu.objects.filter(status=True).filter(type=0).filter(system_type=1).order_by('order')
    menus2 = Menu.objects.filter(status=True).filter(Q(type=0) | Q(type=3)).filter(system_type=2).order_by('order')

    if user.is_moderator:
        moderator = get_object_or_404(Moderator, user=user)
        if moderator.upload_type.id == 2:
            menus2 = menus2.exclude(url_name='text_to_speech')
        if moderator.upload_type.id == 1 and (moderator.is_moderator is False):
            menus2 = menus2.exclude(url_name='moderator_dashboard')

    menu_list0 = []
    menu_list1 = []
    menu_list2 = []

    levels = []
    if user.is_admin:
        levels.append(1)
    if user.is_editor:
        levels.append(2)
    if user.is_reviewer:
        levels.append(3)
    if user.is_author:
        levels.append(4)
    if user.is_expert:
        levels.append(5)
    if user.is_moderator:
        levels.append(6)
    if user.is_out_expert:
        levels.append(7)
    if user.is_pupil:
        levels.append(8)
    if user.is_translator:
        levels.append(9)
    if user.is_admin1:
        levels.append(10)

    for level in levels:
        for menu in menus0:
            if level in menu.get_levels():
                if menu.id not in menu_list0:
                    menu_list0.append(menu.id)
    for level in levels:
        for menu in menus1:
            if level in menu.get_levels():
                if menu.id not in menu_list1:
                    menu_list1.append(menu.id)

    for level in levels:
        for menu in menus2:
            if level in menu.get_levels():
                if menu.id not in menu_list2:
                    menu_list2.append(menu.id)

    items0 = menus0.filter(id__in=menu_list0)
    items1 = menus1.filter(id__in=menu_list1)
    items2 = menus2.filter(id__in=menu_list2)

    lang = get_language()
    data = {
        "menus0": list(items0.values(
            'id', 'name', 'icon_name', 'url', 'url_name', 'order', 'system_type', 'type'
        )),
        "menus1": list(items1.values(
            'id', 'name', 'icon_name', 'url', 'url_name', 'order', 'system_type', 'type'
        )),
        "menus2": list(items2.values(
            'id', 'name', 'icon_name', 'url', 'url_name', 'order', 'system_type', 'type'
        )),
        "lang": lang,
    }
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['reviewer', 'editor'])
def load_notif_count(request):
    user = get_object_or_404(User, id=request.user.id)
    uncheck_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
        notification_status_id=1)
    uncheck_reviewer = ReviewerEditor.objects.filter(editor__user=user).filter(status_id=1)

    data = {
        "notif_count": uncheck_notifications.count(),
        "uncheck_reviewer_count": uncheck_reviewer.count(),
    }
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def reviewers_list(request):
    if request.method == 'GET':
        reviewers = Reviewer.objects.all().order_by('id')
        data = {
            "reviewers": reviewers
        }
        return render(request, "user_app/reviewers_list.html", data)
    else:
        return HttpResponse(_("Xatolik yuz berdi!"))


@unauthenticated_user
def login_page(request):
    if request.method == 'POST' and is_ajax(request):
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is None:
                return JsonResponse({
                    "is_captcha": False,
                    "message": _("Login yoki parol to'g'ri kiritilmadi!")
                })
            # input_value = request.POST.get('captcha_1')
            # hash_key = request.POST.get('captcha_0')
            #
            # if CaptchaStore.objects.filter(hashkey=hash_key).exists():
            #     ob_captcha = get_object_or_404(CaptchaStore, hashkey=hash_key)
            #     if len(str(input_value)) == 0:
            #         return JsonResponse({
            #             "is_captcha": False,
            #             "message": _("Tekshiruv kodini kiriting!")
            #         })
            #
            #     if int(input_value) != int(ob_captcha.response):
            #         return JsonResponse({
            #             "is_captcha": True,
            #             "message": _("Tekshiruv kodi noto'g'ri!")
            #         })
            # else:
            #     return JsonResponse({"is_captcha": True, "message": _(
            #         "Captchani refresh qiling va matematik ifodani qiymatini qayta kiriting!")})
    context = {
        "form": LoginForm(),
    }
    return render(request, "user_app/register/login.html", context=context)


@unauthenticated_user
def register_page(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('chosen_role', '')

        # Parollar mosligini tekshirish
        if password1 != password2:
            return JsonResponse({"success": False, "is_captcha": False, "message": _("Parollar mos emas!")})

        # Username validatsiyasi
        res_username = validate_username(username)
        if not res_username['success']:
            return JsonResponse({"success": False, "is_captcha": False, "message": res_username['reason']})

        # Parol validatsiyasi
        if len(password1) < 8:
            return JsonResponse({"success": False, "is_captcha": False, "message": _("Parol kamida 8 ta belgidan iborat bo'lishi kerak!")})

        if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$])[\w\d!@#$]{8,}$", password1):
            return JsonResponse({
                "success": False,
                "is_captcha": False,
                "message": _("Parolda kamida 1 ta katta harf, kichik harf, raqam va maxsus belgilar (!@#$) bo'lishi kerak.")
            })

        # CAPTCHA tekshiruvi
        input_value = request.POST.get('captcha_1', '')
        hash_key = request.POST.get('captcha_0', '')
        captcha_qayta_kiritilsin = _("Captchani yangilab, ifoda javobini qayta kiriting!")

        if not CaptchaStore.objects.filter(hashkey=hash_key).exists():
            return JsonResponse({"success": False, "is_captcha": True, "message": captcha_qayta_kiritilsin})

        ob_captcha = get_object_or_404(CaptchaStore, hashkey=hash_key)
        if not input_value:
            return JsonResponse({"success": False, "is_captcha": True, "message": _("Tekshiruv kodini kiriting!")})
        if input_value != ob_captcha.response:
            return JsonResponse({"success": False, "is_captcha": True, "message": _("Tekshiruv kodi noto‘g‘ri!")})

        # Forma validatsiyasi
        if not form.is_valid():
            return JsonResponse({"success": False, "is_captcha": False, "message": _("Forma noto‘g‘ri to‘ldirilgan!")})

        # Foydalanuvchini yaratish
        user = form.save(commit=False)
        user.save()

        try:
            if user.chosen_role.code_name == 'author':
                user.system_type = 1
            elif user.chosen_role.code_name == 'pupil':
                user.system_type = 3
                Pupil.objects.create(user=user)
            elif user.chosen_role.code_name == 'out_expert':
                user.system_type = 2
                Teacher.objects.create(user=user, token_for_pupil=generate_token())

            user.save()
            user.roles.add(user.chosen_role)
        except Exception as e:
            return JsonResponse({"success": False, "is_captcha": False, "message": str(e)})

        # Login qilish
        user = authenticate(request, username=user.username, password=password1)
        if user:
            login(request, user)
            return JsonResponse({"success": True, "is_captcha": False, "message": _("Ro'yxatdan muvaffaqiyatli o'tdingiz!")})
        else:
            return JsonResponse({"success": False, "is_captcha": False, "message": _("Avtorizatsiya xatosi!")})

    # GET method
    form = CreateUserForm()
    context = {
        'form': form,
        'roles': Role.objects.filter(code_name__in=['author', 'out_expert']).order_by('level'),
    }
    return render(request, "user_app/register/register.html", context)

@login_required(login_url='login')
def choose_roles(request):
    user = User.objects.get(pk=request.user.id)
    if request.method == "POST" and is_ajax(request):
        form = AddReviewerForm(request.POST)
        files = request.FILES.getlist('file')
        sections = request.POST.getlist('section')
        editor = Editor.objects.all().last()
        status = ReviewerEditorStatus.objects.get(pk=1)

        if not user.is_full_personal_data:
            return JsonResponse({"result": False, "message": _("Shaxsiy ma'lumotlariz to'liq emas!")})
        if len(sections) == 0:
            return JsonResponse({"result": False, "message": _("Ruknni yarating!")})
        if len(files) == 0:
            return JsonResponse({"result": False, "message": _("Iltimos faylni yuklang!")})

        if form.is_valid():
            reviewer = form.save(commit=False)
            reviewer.scientific_degree_id = user.sc_degree.id
            reviewer.save()

            for section_id in sections:
                section = Section.objects.get(pk=int(section_id))
                reviewer.section.add(section)

            for f in files:
                validator = FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf'])
                try:
                    validator(f)
                except ValidationError:
                    return JsonResponse(
                        {"result": False, "message": _("Faqat .doc, .docx yoki .pdf fayllarga ruxsat beriladi!")})

                ReviewerFile.objects.create(
                    reviewer=reviewer,
                    file=f
                )

            ReviewerEditor.objects.create(
                reviewer=reviewer,
                editor=editor,
                status=status,
            )

            return JsonResponse({"result": True, "message": _("Muvaffaqiyatli yuborildi!")})
        else:
            return JsonResponse({"result": False, "message": _("Forma to'liq emas!")})
    context = {
        'user': user,
        'form': AddReviewerForm(),
        'fileForm': ReviewerFileForm(),
    }
    return render(request, "user_app/register/add_reviewer_form.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def reviewer_role_list(request):
    submissions = ReviewerEditor.objects.all().order_by('id')
    context = {
        "submissions": submissions
    }
    return render(request, "user_app/reviewer_list_by_editor.html", context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def reviewer_role_list_detail(request, pk):
    reviewer = Reviewer.objects.get(pk=pk)
    files = ReviewerFile.objects.filter(reviewer=reviewer)
    if request.method == 'POST' and is_ajax(request):
        result = request.POST.get('result')
        submisson = ReviewerEditor.objects.filter(reviewer=reviewer).last()
        if int(result) == 0:
            role = Role.objects.get(pk=3)
            reviewer.is_reviewer = False
            reviewer.user.roles.remove(role)
            reviewer.save()
            submisson.status = ReviewerEditorStatus.objects.get(pk=3)
            submisson.save()

        elif int(result) == 1:
            role = Role.objects.get(pk=3)
            reviewer.is_reviewer = True
            reviewer.user.roles.add(role)
            reviewer.save()
            submisson.status = ReviewerEditorStatus.objects.get(pk=2)
            submisson.save()
        else:
            print("Error")
        return JsonResponse({"message": _("Muvaffaqiyatli bajarildi!")})
    context = {
        "reviewer": reviewer,
        "files": files,
    }
    return render(request, "user_app/crud/check_role_reviewer_form.html", context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST' and is_ajax(request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            data = {
                "result": "ok",
            }
            return JsonResponse(data)
        else:
            data = {
                "result": "bad",
                "message": _("Quyidagi xatoni tuzating."),
            }
            return JsonResponse(data)
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'user_app/register/change_password.html', {
            'form': form,
        })


@login_required(login_url='login')
@orientation_user
# @allowed_users(['admin', 'editor', 'reviewer', 'author'])
def user_dashboard(request):
    user = get_object_or_404(User, pk=request.user.id)
    myqueues = Article.objects.filter(author=user).filter(
        Q(article_status_id=1) | Q(article_status_id=4) | Q(article_status_id=5) | Q(article_status_id=6) |
        Q(article_status_id=7) | Q(article_status_id=8) | Q(article_status_id=10)).order_by('-updated_at')

    myarchives = Article.objects.filter(author=user).filter(
        Q(article_status_id=2) | Q(article_status_id=3) | Q(article_status_id=9)).order_by(
        '-updated_at')
    finished_articles = Article.objects.filter(author=user).filter(
        Q(article_status_id=2) | Q(article_status_id=3)).order_by('-updated_at')

    finished_article = None
    if finished_articles.count() > 0:
        finished_article = finished_articles.last()

    exmpl_files = TemplateFile.objects.filter(code_name=0).all()
    exmpl_file = None
    if exmpl_files.count() == 0:
        exmpl_file = ''
    else:
        exmpl_file = exmpl_files.last()

    context = {
        'user': user,
        'myqueues': myqueues,
        'myqueues_count': myqueues.count(),
        'myarchives': myarchives,
        'myarchives_count': myarchives.count(),
        'exmpl_file': exmpl_file,
        'finished_article': finished_article,
    }
    return render(request, "user_app/user_dashboard.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['editor'])
def editor_dashboard(request):
    return render(request, "user_app/editor_dashboard.html")


@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_dashboard(request):
    return render(request, "user_app/reviewer_dashboard.html")


@login_required(login_url='login')
@allowed_users(role=['editor'])
def editor_notifications(request):
    if request.method == 'GET' and is_ajax(request):
        user = User.objects.get(id=request.user.id)

        new_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
            notification_status_id=1).order_by('-id')

        checking_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(notification_status_id=2).filter(article__is_publish=False, article__is_publish_journal=False).order_by('-id')

        checked_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
            notification_status_id=3).filter(article__is_publish=True, article__is_publish_journal=False).order_by('-id')

        published_articles = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
            notification_status_id=3).filter(article__is_publish=True, article__is_publish_journal=True).order_by(
            '-id')

        rejected_articles = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
            notification_status_id=3).filter(
            Q(article__article_status__key=3) | Q(article__article_status__key=9)).order_by('-id')


        lang = get_language()
        url = f"/{lang}/profile/editor_check_article/"
        if lang == 'uz':
            url = f"/profile/editor_check_article/"

        data = {
            "new_notifications": list(new_notifications.values(
                'id', 'created_at', 'article__id', 'article__title', 'notification_status__id',
                'notification_status__name',
                'article__author__email', 'is_update_article', 'article__article_status__key',
                'article__article_status__name'
            )),
            "checking_notifications": list(checking_notifications.values(
                'id', 'created_at', 'article__id', 'article__title', 'notification_status__id',
                'notification_status__name',
                'article__author__email', 'is_update_article', 'article__article_status__key',
                'article__article_status__name'
            )),
            "checked_notifications": list(checked_notifications.values(
                'id', 'created_at', 'article__id', 'article__title', 'notification_status__id',
                'notification_status__name',
                'article__author__email', 'is_update_article', 'article__article_status__key',
                'article__article_status__name'
            )),
            "published_articles": list(published_articles.values(
                'id', 'created_at', 'article__id', 'article__title', 'notification_status__id',
                'notification_status__name',
                'article__author__email', 'is_update_article', 'article__article_status__key',
                'article__article_status__name'
            )),
            "rejected_articles": list(rejected_articles.values(
                'id', 'created_at', 'article__id', 'article__title', 'notification_status__id',
                'notification_status__name',
                'article__author__email', 'is_update_article', 'article__article_status__key',
                'article__article_status__name'
            )),
            "url": url,
        }

        return JsonResponse(data)

@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_notifications(request):
    user = User.objects.get(id=request.user.id)

    uncheck_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
        Q(notification_status_id=1) | Q(notification_status_id=2)).order_by('-created_at')

    check_notifications = Notification.objects.filter(to_user=user).filter(is_update_article=True).filter(
        notification_status_id=3).order_by('-created_at')

    lang = get_language()
    url = f"/{lang}/profile/reviewer_check_article/"
    if lang == 'uz':
        url = f"/profile/reviewer_check_article/"

    data = {
        "uncheck_notifications": list(uncheck_notifications.values(
            'id', 'created_at', 'article__id', 'article__title', 'notification_status__id', 'notification_status__name',
            'is_update_article', 'from_user__email', 'message'
        )),
        "check_notifications": list(check_notifications.values(
            'id', 'created_at', 'article__id', 'article__title', 'notification_status__id', 'notification_status__name',
            'is_update_article', 'from_user__email', 'message'
        )),
        "url": url,
    }

    return JsonResponse(data)




@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def author_vs_editor_vs_reviewer(request, pk):
    article = Article.objects.get(pk=pk)
    user = get_object_or_404(User, pk=request.user.id)
    current_user_id = user.id
    author_id = article.author.id

    lang = get_language()

    url = f"/{lang}/send_message/"
    if lang == 'uz':
        url = f"/send_message/"

    if request.method == "GET" and is_ajax(request):
        current_user_from = Notification.objects.filter(
            article_id=pk).filter(from_user_id=current_user_id)

        current_user_to = Notification.objects.filter(
            article_id=pk).filter(to_user_id=current_user_id)

        notifications = current_user_from.union(
            current_user_to).order_by('created_at')

        messages = Notification.objects.filter(
            article=article).filter(is_update_article=False)

        for item in messages:
            item.notification_status = NotificationStatus.objects.get(pk=3)
            item.save()

        data = {
            "article_title": article.title,
            "url": url,
            "current_user_id": current_user_id,
            "author_id": author_id,
            "is_visible_comment": True,
            "notifications": list(
                notifications.values(
                    'id', 'article__id', 'from_user__username', 'from_user__email', 'from_user__id', 'message',
                    'to_user__username', 'to_user__email', 'to_user__id', 'created_at',
                )
            ),
        }
        return JsonResponse(data)


@login_required(login_url='login')
def load_notification(request):
    if request.method == 'GET':
        user = User.objects.get(pk=request.user.id)

        uncheck_notifications = Notification.objects.all().order_by("-created_at").filter(to_user=user).filter(
            Q(notification_status_id=1) | Q(notification_status_id=2))
        check_notifications = Notification.objects.all().order_by("-created_at").filter(to_user=user).filter(
            Q(notification_status_id=3))

        data = {
            "uncheck_notifications": list(uncheck_notifications.values(
                'id', 'from_user__avatar', 'from_user__first_name', 'from_user__last_name',
                'created_at'
            )),
            "check_notifications": list(check_notifications.values(
                'id', 'from_user__avatar', 'from_user__first_name', 'from_user__last_name',
                'created_at'
            ))
        }

        return JsonResponse(data)
    else:
        return JsonResponse("Error")


@login_required(login_url='login')
def count_notification(request):
    if request.method == 'GET':
        user = User.objects.get(pk=request.user.id)

        unread_notifications = Notification.objects.all().order_by("-created_at").filter(to_user=user).filter(
            notification_status_id=1)
        count_unread_notifications = unread_notifications.count()
        notifications = unread_notifications[:5]

        return JsonResponse(
            {"count_unread_notifications": count_unread_notifications,
             "notifications": list(notifications.values(
                 'id', 'from_user__avatar', 'from_user__first_name', 'from_user__last_name',
                 'created_at'
             ))})

@login_required(login_url='login')
@allowed_users(role=['editor'])
def editor_check_article(request, pk):
    if request.method == 'GET' and is_ajax(request):
        user = get_object_or_404(User, pk=request.user.id)
        objs = Editor.objects.filter(user=user)
        if objs.count() != 1:
            return render(request, 'user_app/not_access.html')

        notifification = get_object_or_404(Notification, pk=pk)
        if notifification.notification_status.id == 1:
            notifification.notification_status = NotificationStatus.objects.get(id=2)
            notifification.save()
        article = Article.objects.get(pk=notifification.article.id)

        file = ArticleFile.objects.filter(article=article).filter(file_status=1).last()
        article_reviews = ReviewerArticle.objects.filter(article=article).filter(editor=objs.first())

        is_ready_publish: bool = False
        is_ready_rejected: bool = False
        is_ready_resubmit: bool = False
        is_ready_resubmit_extra_reviewer: bool = False

        results_list = []
        confirm = {1}
        reject = {3}
        resubmit1 = {2}
        resubmit2 = {1, 2}
        resubmit_extra1 = {1, 3}
        resubmit_extra2 = {2, 3}
        resubmit_extra3 = {1, 2, 3}

        for item in article_reviews:
            if item.is_extra:
                if item.result == 1:
                    is_ready_publish = True
                elif item.result == 3:
                    is_ready_rejected = True
                elif item.result == 2:
                    is_ready_resubmit = True
            else:
                results_list.append(item.result)

        if set(results_list) == confirm:
            if article_reviews.count() > len(results_list):
                is_ready_publish = False
            if article_reviews.count() == len(results_list):
                is_ready_publish = True

            if article.article_status.id == 4:
                article.article_status = get_object_or_404(ArticleStatus, pk=5)
                article.save()

        if set(results_list) == reject:
            if article_reviews.count() > len(results_list):
                is_ready_rejected = False
            if article_reviews.count() == len(results_list):
                is_ready_rejected = True

            if article.article_status.id == 4:
                article.article_status = get_object_or_404(ArticleStatus, pk=5)
                article.save()

        if set(results_list) == resubmit1 or set(results_list) == resubmit2:
            if article_reviews.count() > len(results_list):
                is_ready_resubmit = False
            if article_reviews.count() == len(results_list):
                is_ready_resubmit = True

            if article.article_status.id == 4:
                article.article_status = get_object_or_404(ArticleStatus, pk=5)
                article.save()

        if set(results_list) == resubmit_extra1 or set(results_list) == resubmit_extra2 or set(
                results_list) == resubmit_extra3:
            if article_reviews.count() > len(results_list):
                is_ready_resubmit_extra_reviewer = False
            if article_reviews.count() == len(results_list):
                is_ready_resubmit_extra_reviewer = True
            if article.article_status.id == 4:
                article.article_status = get_object_or_404(ArticleStatus, pk=5)
                article.save()

        data = {
            "article": article,
            "article_reviews": article_reviews,
            "article_file": file,
            "notif_id": pk,
            "is_ready_publish": is_ready_publish,
            "is_ready_rejected": is_ready_rejected,
            "is_ready_resubmit": is_ready_resubmit,
            "is_ready_resubmit_extra_reviewer": is_ready_resubmit_extra_reviewer,
        }
        html = render_to_string('user_app/check_article_by_editor.html', data, request=request)
        return HttpResponse(html)
    else:
        return redirect('dashboard')


@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_check_article(request, pk):
    if request.method == 'GET' and is_ajax(request):
        user = get_object_or_404(User, pk=request.user.id)
        objs = Reviewer.objects.filter(user=user).filter(is_reviewer=True)

        notifification = get_object_or_404(Notification, pk=pk)
        if notifification.notification_status.id == 1:
            notifification.notification_status = NotificationStatus.objects.get(id=2)
            notifification.save()

        reviewer = get_object_or_404(Reviewer, user=user)
        article = Article.objects.get(pk=notifification.article.id)

        article_reviews = ReviewerArticle.objects.filter(article=article).filter(reviewer=objs.first())

        if article_reviews.count() == 1:
            article_review = article_reviews.first()
            if article_review.status.id == 1:
                article_review.status = StatusReview.objects.get(pk=2)
                article_review.save()
            context = {
                "article": article,
                "notifification": notifification,
                "editor": article_review.editor,
                "article_review": article_review,
                "form": ReviewArticleForm(instance=article_review)
            }
            return render(request, 'user_app/check_article_by_reviewer.html', context=context)
        else:
            return HttpResponse("Error")
    else:
        return redirect('dashboard')


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def load_reviewers(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    authors = ExtraAuthor.objects.filter(article=article)
    emails = []
    for author in authors:
        emails.append(author.email)
    reviewers = Reviewer.objects.filter(is_reviewer=True).exclude(user__email__in=emails)

    data = {
        "reviewers": list(reviewers.values(
            'id', 'user__id', 'user__first_name', 'user__last_name', 'user__email', 'scientific_degree__name',
            'user__middle_name'
        ))
    }
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_confirmed(request, pk):
    if request.method == 'POST' and is_ajax(request):
        review = get_object_or_404(ReviewerArticle, pk=pk)
        form = ReviewArticleForm(request.POST, instance=review)
        if form.is_valid():
            ob = form.save(commit=False)
            ob.result = 1
            ob.status = StatusReview.objects.get(pk=3)
            ob.save()

            notif = get_object_or_404(Notification, pk=int(ob.notification.id))
            notif.notification_status = get_object_or_404(NotificationStatus, pk=3)
            notif.save()

            data = {
                "result": True,
                "message": _("Muvaffaqiyatli tasdiqlandi!"),
            }
            return JsonResponse(data=data)
        else:
            data = {
                "result": False,
                "message": _("Xatolik yuz berdi!"),
            }
            return JsonResponse(data=data)
    else:
        return HttpResponse(_("Sahifa topilmadi!"))


@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_resubmit(request):
    if request.method == 'POST' and is_ajax(request):
        review_id = request.POST.get('review_article_id')
        notif_id = request.POST.get('notif_id')
        comment = request.POST.get('comment')

        with open('error.txt', 'w') as f:
            f.write(f"{review_id}")
            f.write(f"{notif_id}")

        review = ReviewerArticle.objects.get(pk=int(review_id))
        review.comment = comment
        review.result = 2
        review.status = StatusReview.objects.get(pk=5)
        review.save()

        article = get_object_or_404(Article, pk=review.article.id)

        notif = get_object_or_404(Notification, pk=int(notif_id))
        notif.notification_status = get_object_or_404(NotificationStatus, pk=3)
        notif.save()

        Notification.objects.create(
            article=article,
            from_user=review.reviewer.user,
            to_user=review.editor.user,
            message=comment,
            notification_status=NotificationStatus.objects.get(id=1),
        )

        data = {
            "message": _("Maqolani qayta yuborish muvaffaqiyatli amalga oshirildi!"),
        }
        return JsonResponse(data=data)
    else:
        return HttpResponse(_("Sahifa topilmadi!"))


@login_required(login_url='login')
@allowed_users(role=['reviewer'])
def reviewer_rejected(request):
    if request.method == 'POST' and is_ajax(request):
        review_id = request.POST.get('review_article_id')
        notif_id = request.POST.get('notif_id')
        comment = request.POST.get('comment')

        review = ReviewerArticle.objects.get(pk=int(review_id))
        review.comment = comment
        review.result = 3
        review.status = StatusReview.objects.get(pk=4)
        review.save()

        article = get_object_or_404(Article, pk=review.article.id)

        notif = get_object_or_404(Notification, pk=int(notif_id))
        notif.notification_status = get_object_or_404(NotificationStatus, pk=3)
        notif.save()

        Notification.objects.create(
            article=article,
            from_user=review.reviewer.user,
            to_user=review.editor.user,
            message=comment,
            notification_status=NotificationStatus.objects.get(id=1),
        )
        data = {
            "message": _("Muvaffaqiyatli bajarildi!"),
        }
        return JsonResponse(data=data)
    else:
        return HttpResponse(_("Sahifa topilmadi"))


@login_required(login_url='login')
@allowed_users(role=['editor'])
def editor_resubmit_to_reviewer(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        review_id = request.POST.get('review_id')
        review = ReviewerArticle.objects.get(pk=int(review_id))
        review.result = 0
        review.status = StatusReview.objects.get(pk=1)
        review.save()

        article = get_object_or_404(Article, pk=review.article.id)
        article.article_status = get_object_or_404(ArticleStatus, pk=4)
        article.save()

        Notification.objects.create(
            article=article,
            from_user=user,
            to_user=review.reviewer.user,
            message=_("Hurmatli taqrizchi sizga maqola qayta yuborildi"),
            notification_status=NotificationStatus.objects.get(id=1),
            is_update_article=True,
        )
        data = {
            "message": _("Taqrizchiga qayta yuborildi!"),
        }
        return JsonResponse(data=data)
    else:
        return HttpResponse(_("Sahifa topilmadi"))


@login_required(login_url='login')
@allowed_users(role=['editor'])
def approve_publish(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        data = None
        article_id = request.POST.get('article_id')
        notif_id = request.POST.get('notif_id')
        btn_number = int(request.POST.get('btn_number'))
        token = request.POST['csrfmiddlewaretoken']

        article = get_object_or_404(Article, pk=int(article_id))
        notif = get_object_or_404(Notification, pk=int(notif_id))

        d = {'user': article.author, 'article': article}
        subject = _(
            "O'zbekiston respublikasi, oliy ta'lim, fan va innovatsiyalar vazirligi huzuridagi bilim va "
            "malakalarni baholash agentligi online axborotnoma jurnali.")
        to_email = article.author.email

        if btn_number == 0:
            article.article_status = ArticleStatus.objects.get(pk=2)
            article.is_publish = True
            article.save()

            if notif.notification_status.id == 2:
                notif.notification_status = NotificationStatus.objects.get(id=3)
                notif.save()

            msg = ''
            r_articles = ReviewerArticle.objects.filter(article=article).order_by('id')
            i = 1
            for r in r_articles:
                msg += f"{i}-TAQRIZ. {r.comment}\n\n"
                i += 1

            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=msg,
                notification_status=NotificationStatus.objects.get(id=1),
            )

            # template = 'user_app/Email_confirm.html'
            #             # send_message_email(template=template, data=d, to_email=to_email, subject=subject)

            data = {
                "message": _("Maqola muvaffaqiyatli tasdiqlandi!"),
            }
        elif btn_number == 1:
            article.article_status = ArticleStatus.objects.get(pk=3)
            article.save()

            if notif.notification_status.id == 2:
                notif.notification_status = NotificationStatus.objects.get(id=3)
                notif.save()

            msg = ''
            r_articles = ReviewerArticle.objects.filter(article=article).order_by('id')
            i = 1
            for r in r_articles:
                msg += f"{i}-TAQRIZ. {r.comment}\n\n"
                i += 1

            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=msg,
                notification_status=NotificationStatus.objects.get(id=1),
            )

            template = 'user_app/Email_reject.html'
            send_message_email(template=template, data=d, to_email=to_email, subject=subject)

            data = {
                "message": _("Maqola Rad Etildi!"),
            }
        elif btn_number == 2:
            text = request.POST.get('text')
            article.article_status = get_object_or_404(ArticleStatus, pk=8)
            article.is_resubmit = True
            article.save()

            msg = ''
            r_articles = ReviewerArticle.objects.filter(article=article).order_by('id')
            i = 1
            for r in r_articles:
                msg += f"{i}-TAQRIZ. {r.comment}\n\n"
                i += 1

            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=text,
                notification_status=NotificationStatus.objects.get(id=1),
            )
            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=msg,
                notification_status=NotificationStatus.objects.get(id=1),
            )
            data = {
                "message": _("Muallifga maqolani qayta yuborish uchun yuborildi!"),
            }
        elif btn_number == 3:
            article_section = article.section
            editor = get_object_or_404(Editor, user=user)
            authors = ExtraAuthor.objects.filter(article=article)

            author_levels = []
            for author in authors:
                author_levels.append(author.scientific_degree.level)

            max_level_author = max(author_levels)

            reviewers = Reviewer.objects.filter(is_reviewer=True).filter(
                scientific_degree__level__gte=max_level_author)

            reviewers_id = []
            if reviewers.count() > 0:
                for reviewer in reviewers:
                    results = ReviewerArticle.objects.filter(article=article).filter(reviewer=reviewer)
                    if results.count() == 0:
                        sections = []
                        for it in reviewer.section.all():
                            sections.append(it.id)
                        if article_section.id in sections:
                            reviewers_id.append(reviewer.id)
                    else:
                        continue
            else:
                degree = ScientificDegree.objects.get(level=max_level_author)
                data = {
                    "is_valid": False,
                    "message": _(f"Bu maqolaga ilmiy darajasi({degree.name})ga teng taqrizchi topilmadi!"),
                }
                return JsonResponse(data=data)

            if len(reviewers_id) > 0:
                select_random_reviewer = np.random.choice(reviewers_id, 1, replace=False).tolist()
            else:
                data = {
                    "is_valid": False,
                    "message": _(f"{article_section.name} sohasini tekshiradigan taqrizchilar topilmadi!"),
                }
                return JsonResponse(data=data)

            for item in select_random_reviewer:
                reviewer = get_object_or_404(Reviewer, pk=int(item))
                reviewer_user = get_object_or_404(User, pk=reviewer.user.id)

                notif = Notification.objects.create(
                    article=article,
                    from_user=user,
                    to_user=reviewer_user,
                    message=_("Hurmatli taqrizchi sizga maqola yuborildi"),
                    notification_status=NotificationStatus.objects.get(id=1),
                    is_update_article=True,
                )

                ReviewerArticle.objects.create(
                    article=article,
                    editor=editor,
                    reviewer=reviewer,
                    status=StatusReview.objects.get(pk=1),
                    comment="",
                    is_extra=True,
                    notification=notif,
                )

            data = {
                "is_valid": True,
                "select_random_reviewers": select_random_reviewer,
                "message": _("Taqrizchiga muvaffaqiyatli yuborildi!"),
            }

        else:
            print(-1)
        return JsonResponse(data=data)
    else:
        return HttpResponse("Not Fount Page!")


@login_required(login_url='login')
@allowed_users(role=['editor'])
def editor_submit_result(request):  # Taqrizchi natijani muharrirga yuborish bo'limi
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        data = None
        article_id = request.POST.get('article_id')
        notif_id = request.POST.get('notif_id')
        btn_number = int(request.POST.get('btn_number'))
        text = request.POST.get('text')

        token = request.POST['csrfmiddlewaretoken']

        article = get_object_or_404(Article, pk=int(article_id))
        notif = get_object_or_404(Notification, pk=int(notif_id))

        if btn_number == 0:
            article.article_status = ArticleStatus.objects.get(pk=7)
            article.save()

            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=text,
                notification_status=NotificationStatus.objects.get(id=1),
            )

            data = {
                "message": _("Maqola muallifga to'g'irlash uchun yuborildi!"),
            }
        elif btn_number == 1:
            article.article_status = ArticleStatus.objects.get(pk=9)
            article.save()

            if notif.notification_status.id == 2:
                notif.notification_status = NotificationStatus.objects.get(id=3)
                notif.save()

            Notification.objects.create(
                article=article,
                from_user=user,
                to_user=article.author,
                message=text,
                notification_status=NotificationStatus.objects.get(id=1),
            )

            d = {'user': article.author, 'article': article}
            subject = _(
                "O'zbekiston respublikasi, oliy ta'lim, fan va innovatsiyalar vazirligi huzuridagi bilim va "
                "malakalarni baholash agentligi online axborotnoma jurnali.")
            to_email = article.author.email

            template = 'user_app/Email_reject.html'
            # send_message_email(template=template, data=d, to_email=to_email, subject=subject)

            data = {
                "message": _("Maqola Rad Etildi!"),
            }
        else:
            data = {
                "message": _("Bunday buyruq yo'q"),
            }
        return JsonResponse(data=data)
    else:
        return HttpResponse("Not Fount Page!")


@login_required(login_url='login')
@allowed_users(role=['editor'])
def sending_reviewer(request):  # Tanlangan taqrizchilarga yuborish
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST':
        selected = request.POST.getlist('reviewers[]')
        token = request.POST.get('csrfmiddlewaretoken')
        article_id = request.POST['article_id']

        if len(selected) > 0 and token and article_id:
            article = Article.objects.get(pk=int(article_id))
            editor = get_object_or_404(Editor, user=user)

            for item in selected:
                reviewer = get_object_or_404(Reviewer, pk=int(item))
                reviewer_user = get_object_or_404(User, pk=reviewer.user.id)
                reviews = ReviewerArticle.objects.filter(article=article).filter(reviewer=reviewer)

                if article.author.id == reviewer_user.id:
                    continue

                if reviews.count() == 0:
                    notif = Notification.objects.create(
                        article=article,
                        from_user=user,
                        to_user=reviewer_user,
                        message=_("Hurmatli taqrizchi sizga maqola yuborildi"),
                        notification_status=NotificationStatus.objects.get(id=1),
                        is_update_article=True,
                    )

                    ReviewerArticle.objects.create(
                        article=article,
                        editor=editor,
                        reviewer=reviewer,
                        status=StatusReview.objects.get(pk=1),
                        comment="",
                        notification=notif,
                    )
                else:
                    continue

            article.article_status = get_object_or_404(ArticleStatus, pk=4)
            article.save()
            data = {
                "is_valid": True,
                "select_random_reviewers": selected,
                "message": _("Taqrizchilarga muvaffaqiyatli yuborildi!"),
            }
            return JsonResponse(data=data)
        else:
            data = {
                "is_valid": False,
                "message": _("Taqrizchilarni tanlamadingiz!"),
            }
            return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['editor'])
def random_sending_reviewer(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST':
        number = request.POST['value']
        article_id = request.POST['article_id']
        token = request.POST['csrfmiddlewaretoken']

        if int(number) > 0 and token and article_id:
            article = Article.objects.get(pk=int(article_id))
            article_section = article.section
            editor = get_object_or_404(Editor, user=user)
            authors = ExtraAuthor.objects.filter(article=article)

            author_levels = []
            authors_email = []
            for author in authors:
                authors_email.append(author.email)
                author_levels.append(author.scientific_degree.level)

            max_level_author = max(author_levels)

            reviewers = Reviewer.objects.filter(is_reviewer=True).filter(
                scientific_degree__level__gte=max_level_author).exclude(user__email__in=authors_email)

            reviewers_id = []
            if reviewers.count() > 0:
                for reviewer in reviewers:
                    reviews = ReviewerArticle.objects.filter(article=article).filter(reviewer=reviewer)
                    if article.author.id == reviewer.user.id:
                        continue
                    if reviews.count() == 0:
                        sections = []
                        for it in reviewer.section.all():
                            sections.append(it.id)
                        if article_section.id in sections:
                            reviewers_id.append(reviewer.id)
                    else:
                        continue
            else:
                degree = ScientificDegree.objects.get(level=max_level_author)
                data = {
                    "is_valid": False,
                    "message": _(f"Bu maqolaga ilmiy darajasi({degree.name})ga teng taqrizchilar topilmadi!"),
                }
                return JsonResponse(data=data)

            if len(reviewers_id) > 0:
                if len(reviewers_id) >= int(number):
                    select_random_reviewers = np.random.choice(reviewers_id, int(number), replace=False).tolist()
                else:
                    data = {
                        "is_valid": False,
                        "message": _(
                            f"Topilgan taqrizchilar soni {len(reviewers_id)} ga teng. Siz izlagan son {number} ga teng!"),
                    }
                    return JsonResponse(data=data)
            else:
                data = {
                    "is_valid": False,
                    "message": _(f"{article_section.name} sohasini tekshiradigan taqrizchilar topilmadi!"),
                }
                return JsonResponse(data=data)

            for item in select_random_reviewers:
                reviewer = get_object_or_404(Reviewer, pk=int(item))
                reviewer_user = get_object_or_404(User, pk=reviewer.user.id)

                if article.author.id == reviewer_user.id:
                    continue

                notif = Notification.objects.create(
                    article=article,
                    from_user=user,
                    to_user=reviewer_user,
                    message=_("Hurmatli taqrizchi sizga maqola yuborildi"),
                    notification_status=NotificationStatus.objects.get(id=1),
                    is_update_article=True,
                )

                ReviewerArticle.objects.create(
                    article=article,
                    editor=editor,
                    reviewer=reviewer,
                    status=StatusReview.objects.get(pk=1),
                    comment="",
                    notification=notif
                )

            article.article_status = get_object_or_404(ArticleStatus, pk=4)
            article.save()
            data = {
                "is_valid": True,
                "select_random_reviewers": select_random_reviewers,
                "message": _("Taqrizchilarga muvaffaqiyatli yuborildi!"),
            }
            return JsonResponse(data=data)
        else:
            data = {
                "is_valid": False,
                "message": _("Taqrizchilarni to'liq tanlang!"),
            }
            return JsonResponse(data=data)


@login_required(login_url='login')
def edit_profile(request):
    user = get_object_or_404(User, pk=request.user.id)
    teacher = None
    if Teacher.objects.filter(user=user).exists():
        teacher = get_object_or_404(Teacher, user=user)

    if request.method == 'POST' and is_ajax(request):
        form = UpdateUserForm(request.POST, request.FILES, instance=user)

        if not form.has_changed():
            return JsonResponse({'status': False, "message": _("Forma ma'lumotlarida o'zgarish yo'q!")})

        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, "message": _("Ma'lumotlariz muvaffaqiyatli saqlandi.")})
        else:
            return JsonResponse({'status': False, "message": _("Forma to'liq emas!")})
    else:
        form = UpdateUserForm(instance=user)
        roles = Role.objects.all().order_by('-id')
        res = Reviewer.objects.filter(user=user).exists()
        context = {"user": user, "teacher": teacher, 'form': form, 'roles': roles, "is_send_request": res}
        return render(request, 'user_app/register/edit_profile.html', context)


@login_required(login_url='login')
def get_data_ps(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        jshshr = request.POST.get('jshshir')
        ps = request.POST.get('pasport')
        ps = str(ps).replace(' ', '')

        if jshshr == '' or ps == '':
            data = {
                'message': "Ma'lumot to'liqmas!"
            }
            return JsonResponse(data)

        try:
            url = f"https://imei_api.uzbmb.uz/compress?imie={jshshr}&ps={ps.upper()}"
            response = requests.get(url, verify=False, timeout=3)

            data = json.loads(response.text)
        except Exception as e:
            d = {
                'result': False,
                'message': f"API serverida xatolik yuz berdi! {e}"
            }
            return JsonResponse(d)

        if data['status'] == 1:
            data = data['data']
            user.jshshr = data['pnfl']
            user.pser = data['ps_ser']
            user.pnum = data['ps_num']

            if User.objects.filter(jshshr=data['pnfl'], pser=data['ps_ser'], pnum=data['ps_num'],
                                   system_type=user.system_type).exists():
                d = {
                    'result': False,
                    'message': "Kechirasiz, siz tizimda mavjudsiz."
                }
                return JsonResponse(d)

            user.last_name = data['sname']
            user.first_name = data['fname']
            user.middle_name = data['mname']
            user.birthday = data['birth_date']
            user.avatar = data['photo']

            tuman = data['birth_place']
            s = str(data['doc_give_place']).split(' ')
            s1 = s[-2] + ' ' + s[-1]

            if not Region.objects.filter(name=s1).exists():
                r_ob = Region.objects.create(name=s1)
                user.region = r_ob
            else:
                user.region = get_object_or_404(Region, name=s1)

            user.save()

            ds = District.objects.filter(name=tuman).exists()

            if not ds:
                ob = District.objects.create(name=tuman, region=user.region)
                user.district = ob
            else:
                user.district = get_object_or_404(District, name=tuman)

            if data['sex'] == 1:
                user.gender_id = 1
            elif data['sex'] == 2:
                user.gender_id = 2
            else:
                pass

            user.save()
            d = {
                'result': True,
                'message': "Muvaffaqiyatli yangilandi."
            }
            return JsonResponse(d)

        if data['status'] == 0:
            d = {
                'result': False,
                'message': f"Xatolik: {data['data']['message']}"
            }
            return JsonResponse(d)
    else:
        return render(request, "user_app/register/get_ps_data.html")


@login_required(login_url='login')
@allowed_users(role=['admin'])
def view_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {
        "user": user,
    }
    return render(request, 'user_app/crud/view_user.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        selected = list(request.POST.getlist('roles[]'))
        token = request.POST['csrfmiddlewaretoken']

        if len(selected) < 1:
            data = {"message": "Rol tanlanmadi!", }
            return JsonResponse(data=data)

        roles_id, _ = user.get_roles
        for item in selected:
            r = get_object_or_404(Role, pk=int(item))
            if r.id in roles_id or r.level == 3:
                continue
            else:
                user.roles.add(r)
                if r.level == 2:
                    if not Editor.objects.filter(user=user).exists():
                        Editor.objects.create(
                            user=user)
                if r.level == 1:
                    user.is_staff = True
                    user.save()
                if r.level == 5:
                    if not Expert.objects.filter(user=user).exists():
                        Expert.objects.create(
                            user=user,
                            is_expert=True,
                            lang_test=get_object_or_404(LanguageTest, pk=2),
                            subject=get_object_or_404(Subject, pk=5),
                            is_have_cert=True,
                        )
                if r.level == 6:
                    if not Moderator.objects.filter(user=user).exists():
                        Moderator.objects.create(
                            user=user,
                            is_moderator=True,
                        )
                if r.level == 10:
                    if not Admin1.objects.filter(user=user).exists():
                        Admin1.objects.create(
                            user=user,
                            is_admin1=True,
                        )
        roles_id, _ = user.get_roles
        arr1 = np.array(roles_id, dtype=np.int64)
        arr2 = np.array(selected, dtype=np.int64)
        res = np.setdiff1d(arr1, arr2)

        for item in res:
            rl = get_object_or_404(Role, pk=int(item))
            if rl.level == 4:
                continue
            if rl.level == 2:
                editor = get_object_or_404(Editor, user=user)
                editor.delete()
            if rl.level == 5:
                expert = get_object_or_404(Expert, user=user)
                expert.delete()
            if rl.level == 6:
                moderator = get_object_or_404(Moderator, user=user)
                moderator.delete()
            if rl.level == 10:
                admin1 = get_object_or_404(Admin1, user=user)
                admin1.delete()
            user.roles.remove(rl)
        data = {
            "message": "Muvaffaqiyatli bajarildi!",
        }
        return JsonResponse(data=data)
    else:
        context = {
            "user": user,
            "roles": Role.objects.all(),
        }
        return render(request, 'user_app/crud/edit_user.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        data = {
            "result": True,
            "message": _("Bu foydalanuvchi muvaffaqiyatli o'chirildi!"),
        }
        return JsonResponse(data=data)
    context = {
        "user": user,
    }
    return render(request, 'user_app/crud/delete_user.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def give_editor_role(request, pk):
    new_editor = get_object_or_404(Editor, pk=pk)
    if request.method == "GET":
        old_editors = Editor.objects.filter(is_editor=True)
        r = get_object_or_404(Role, level=2)
        for it in old_editors:
            old_editor = get_object_or_404(Editor, pk=it.id)
            old_editor.is_editor = False
            old_editor.user.roles.remove(r)
            old_editor.save()
        new_editor.is_editor = True
        new_editor.user.roles.add(r)
        new_editor.save()
        data = {
            "result": True,
            "message": _("Bu muharrir muvaffaqiyatli tasdiqlandi!"),
        }
        return JsonResponse(data=data)
    else:
        data = {
            "result": False,
            "message": _("Xatolik!"),
        }
        return JsonResponse(data=data)


def error_404(request, exception):
    return render(request, 'user_app/error_404.html')


def error_500(request):
    return render(request, 'user_app/handler500.html')


@login_required(login_url='login')
def permission_for_expertise_dashboard(request):
    user = get_object_or_404(User, pk=request.user.id)
    expert = None
    try:
        expert = get_object_or_404(Expert, user=user)
    except Exception as e:
        expert = None
    return render(request, 'user_app/register/permission_for_expertise_dashboard.html', {'user': user, 'expert': expert})
