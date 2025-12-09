import datetime
import re
import subprocess
import sys

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import translation
from django.views.decorators.csrf import requires_csrf_token

from post.models import Post, BlankPage
from user_app.decorators import allowed_users
from article_app.forms import *
from user_app.models import User, Editor, Menu, ReviewerArticle
from journal.models import *

from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls.base import resolve, reverse
from django.urls.exceptions import Resolver404
from django.utils.translation import activate, get_language
from django.utils.translation import gettext_lazy as _
from docx2pdf import convert
import filetype


def is_pdf(path_to_file):
    return filetype.guess(path_to_file).mime == 'application/pdf'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def set_language(request, language):
    global view
    for lang, _ in settings.LANGUAGES:
        translation.activate(lang)
        try:
            view = resolve(urlparse(request.META.get("HTTP_REFERER")).path)
        except Resolver404:
            view = None
        if view:
            break
    if view:
        translation.activate(language)
        next_url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    else:
        response = HttpResponseRedirect("/")
    return response


def main_page(request):
    post = Post.objects.filter(is_publish=True)

    context = {
        'post': post.last(),
    }
    return render(request, "article_app/main.html", context=context)


def last_journal(request):
    journal = Journal.objects.filter(is_publish=True, status=True).order_by('created_at').last()
    return redirect('view_journal', journal.id)


def contact(request):
    connect = BlankPage.objects.filter(is_publish=True, key='contact')
    context = {
        'contact': connect.last(),
    }
    return render(request, "article_app/blank_page/contact.html", context=context)


def technical_support(request):
    ob = BlankPage.objects.filter(is_publish=True, key='technical_support')
    context = {
        'ob': ob.last(),
    }
    return render(request, "article_app/blank_page/technik_service.html", context=context)


def editor_board(request):
    editorial_board = BlankPage.objects.filter(is_publish=True, key='editorial_board')
    context = {
        'editorial_board': editorial_board.last(),
    }
    return render(request, "article_app/blank_page/editor_board.html", context=context)


def about_journal(request):
    about_journals = BlankPage.objects.filter(is_publish=True, key='about_journal')
    context = {
        'about_journal': about_journals.last(),
    }
    return render(request, "article_app/blank_page/about_journal.html", context=context)


def guide_for_authors(request):
    guide_for_author = BlankPage.objects.filter(is_publish=True, key='guide_for_authors')
    context = {
        'guide_for_author': guide_for_author.last(),
    }
    return render(request, "article_app/blank_page/guide_for_authors.html", context=context)


def load_sidebar_menus(request):
    menus = Menu.objects.filter(status=True).filter(type=2).order_by('order')
    lang = get_language()
    data = {
        "menus": list(menus.values(
            'id', 'name', 'icon_name', 'url', 'url_name', 'order'
        )),
        "lang": lang,
    }
    return JsonResponse(data=data)


def load_navbar_menus(request):
    is_authenticated = False
    full_name = None
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        is_authenticated = user.is_authenticated
        full_name = user.full_name
    menus = Menu.objects.filter(status=True).filter(type=1).order_by('order')
    lang = get_language()
    data = {
        "navbar_menus": list(menus.values(
            'id', 'name', 'icon_name', 'url', 'url_name', 'order'
        )),
        "is_authenticated": is_authenticated,
        "full_name": full_name,
        "lang": lang,
    }
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def list_sections(request):
    sections = Section.objects.all().order_by('id')
    context = {
        'objects': sections,
    }
    return render(request, "article_app/sections.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_section(request):
    if request.method == "POST":
        form = CreateSectionForm(request.POST)
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
        form = CreateSectionForm()
        context = {
            'form': form,
        }
        return render(request, "article_app/crud/create_section.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_section(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        form = CreateSectionForm(request.POST, instance=section)
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
        form = CreateSectionForm(instance=section)
        context = {
            'form': form,
            'section': section,
        }
        return render(request, "article_app/crud/edit_section.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_section(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == "POST":
        section.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'section': section,
        }
        return render(request, "article_app/crud/delete_section.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def article_type_list(request):
    objects = ArticleType.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "article_app/article_types.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_article_type(request):
    if request.method == "POST":
        form = CreateArticleTypeForm(request.POST)
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
        form = CreateArticleTypeForm()
        context = {
            'form': form,
        }
        return render(request, "article_app/crud/create_article_type.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_article_type(request, pk):
    article_type = get_object_or_404(ArticleType, pk=pk)
    if request.method == "POST":
        form = CreateStageForm(request.POST, instance=article_type)
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
        form = CreateStageForm(instance=article_type)
        context = {
            'form': form,
            'article_type': article_type,
        }
        return render(request, "article_app/crud/edit_article_type.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_article_type(request, pk):
    article_type = get_object_or_404(ArticleType, pk=pk)
    if request.method == "POST":
        article_type.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'article_type': article_type,
        }
        return render(request, "article_app/crud/delete_article_type.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def article_stages_list(request):
    objects = Stage.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "article_app/article_stages.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_stage(request):
    if request.method == "POST":
        form = CreateStageForm(request.POST)
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
        form = CreateStageForm()
        context = {
            'form': form,
        }
        return render(request, "article_app/crud/create_stage.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_stage(request, pk):
    stage = get_object_or_404(Stage, pk=pk)
    if request.method == "POST":
        form = CreateStageForm(request.POST, instance=stage)
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
        form = CreateStageForm(instance=stage)
        context = {
            'form': form,
            'stage': stage,
        }
        return render(request, "article_app/crud/edit_stage.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_stage(request, pk):
    stage = get_object_or_404(Stage, pk=pk)
    if request.method == "POST":
        stage.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'stage': stage,
        }
        return render(request, "article_app/crud/delete_stage.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def users_list(request):
    objects = User.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "user_app/settings/users.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def article_status_list(request):
    objects = ArticleStatus.objects.all()
    context = {
        'objects': objects,
    }
    return render(request, "article_app/article_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_article_status(request):
    if request.method == "POST":
        form = CreateArticleStatusForm(request.POST)
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
        form = CreateArticleStatusForm()
        context = {
            'form': form,
        }
        return render(request, "article_app/crud/create_article_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_article_status(request, pk):
    article_status = get_object_or_404(ArticleStatus, pk=pk)
    if request.method == "POST":
        form = CreateArticleStatusForm(request.POST, instance=article_status)
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
        form = CreateArticleStatusForm(instance=article_status)
        context = {
            'form': form,
            'article_status': article_status,
        }
        return render(request, "article_app/crud/edit_article_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_article_status(request, pk):
    article_status = get_object_or_404(ArticleStatus, pk=pk)
    if request.method == "POST":
        article_status.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'article_status': article_status,
        }
        return render(request, "article_app/crud/delete_article_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def notification_status_list(request):
    objects = NotificationStatus.objects.all().order_by('id')
    context = {
        'objects': objects,
    }
    return render(request, "article_app/notification_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_notification_status(request):
    if request.method == "POST":
        form = CreateNotificationStatusForm(request.POST)
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
        form = CreateNotificationStatusForm()
        context = {
            'form': form,
        }
        return render(request, "article_app/crud/create_notification_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_notification_status(request, pk):
    notification_status = get_object_or_404(NotificationStatus, pk=pk)
    if request.method == "POST":
        form = CreateNotificationStatusForm(request.POST, instance=notification_status)
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
        form = CreateNotificationStatusForm(instance=notification_status)
        context = {
            'form': form,
            'notification_status': notification_status,
        }
        return render(request, "article_app/crud/edit_notification_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_notification_status(request, pk):
    notification_status = get_object_or_404(NotificationStatus, pk=pk)
    if request.method == "POST":
        notification_status.delete()
        data = {
            "message": _("Muvaffaqiyatli o'chirildi!")
        }
        return JsonResponse(data)
    else:
        context = {
            'notification_status': notification_status,
        }
        return render(request, "article_app/crud/delete_notification_status.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def create_article(request):
    user = User.objects.get(pk=request.user.id)
    if user.birthday is None or user.region is None or user.gender is None or user.phone is None or user.pser is None or user.pnum is None or user.work is None:
        data = {
            "result": False,
            "message": _("Shaxsiy ma'lumotlarizni to'ldiring!"),
        }
        return JsonResponse(data=data)

    if request.method == "POST" and is_ajax(request):
        country = request.POST.get('country', None)
        article_type = request.POST.get('article_type', None)
        article_lang = request.POST.get('article_lang', None)
        section = request.POST.get('section', None)
        title = request.POST.get('title', None)

        form = CreateArticleForm(request.POST)
        if form.is_valid() and country and article_type and article_lang and section and title:
            article = form.save(commit=False)
            article.author = user
            article.article_status_id = 6
            article.save()

            ExtraAuthor.objects.create(
                article=article,
                lname=article.author.last_name,
                fname=article.author.first_name,
                mname=article.author.middle_name,
                email=article.author.email,
                work=article.author.work,
            )
            lang = get_language()

            url = f"/{lang}/article/edit/{article.id}/"
            if lang == 'uz':
                url = f"/article/edit/{article.id}/"
            data = {
                "result": True,
                "message": "Ok!",
                "url": url,
            }
            return JsonResponse(data=data)
        else:
            data = {
                "result": False,
                "message": _("Forma to'ldirishda xatolik yuz berdi!"),
            }
            return JsonResponse(data=data)
    else:
        context = {
            'form': CreateArticleForm(),
        }
        return render(request, "article_app/crud/create_article.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def update_article(request, pk):
    user = request.user
    editor = get_object_or_404(Editor, is_editor=True)
    articles = Article.objects.filter(pk=pk)
    if articles.count() == 0:
        return render(request, 'user_app/not_access.html')

    article = articles.first()
    if user != article.author:
        return render(request, 'user_app/not_access.html')

    if request.method == "POST":
        form = UpdateArticleForm(request.POST, instance=article)

        authors = ExtraAuthor.objects.filter(article=article)
        for author in authors:
            if author.scientific_degree is None or author.work is None:
                data = {
                    'result': False,
                    'message': _("Ilmiy daraja yoki ish joy kiritilmadi!"),
                }
                return JsonResponse(data)

        if form.is_valid():
            files = ArticleFile.objects.filter(
                article=article).filter(file_status=1)
            title = str(request.POST.get('title')).replace(
                '<p>', '').replace('</p>', '')
            title_en = str(request.POST.get('title_en')).replace(
                '<p>', '').replace('</p>', '')
            abstrk = str(request.POST.get('abstract')).replace(
                '<p>', '').replace('</p>', '')
            abstrk_en = str(request.POST.get('abstract_en')).replace(
                '<p>', '').replace('</p>', '')
            keywords = str(request.POST.get('keywords')).replace(
                '<p>', '').replace('</p>', '')
            keywords_en = str(request.POST.get('keywords_en')).replace(
                '<p>', '').replace('</p>', '')

            if len(abstrk) == 0 or len(
                    keywords) == 0 or len(title_en) == 0 or len(title) == 0 or len(abstrk_en) == 0 or len(
                keywords_en) == 0 or files.count() == 0:
                data = {
                    'result': False,
                    'message': _("Formani to'liq to'ldiring!"),
                }
                return JsonResponse(data)

            form.save()

            if article.article_status.id == 6:
                article.article_status = ArticleStatus.objects.get(pk=1)
                article.save()
                Notification.objects.create(
                    article=article,
                    from_user=article.author,
                    to_user=editor.user,
                    message=_("Assalomu aleykum.Yangi maqolamni yubordim!"),
                    notification_status=NotificationStatus.objects.get(id=1),
                    is_update_article=True,
                )

            if article.article_status.id == 7 or article.article_status.id == 8:
                article.article_status = ArticleStatus.objects.get(pk=1)
                article.save()

                notifs = Notification.objects.filter(is_update_article=True).filter(article=article).filter(
                    from_user=article.author).filter(to_user=editor.user)
                if notifs.count() > 0:
                    notif = notifs.last()
                    notif.message = _("Assalomu aleykum.Maqolamni to'g'irlab qayta yubordim!")
                    notif.notification_status = NotificationStatus.objects.get(id=1)
                    notif.save()

                r_articles = ReviewerArticle.objects.filter(article=article).order_by('id')
                for r in r_articles:
                    r.is_resubmit_reviewer = True
                    r.save()

            data = {
                'result': True,
                'message': _("Muvaffaqiyatli amalga oshirildi!"),
            }
            return JsonResponse(data)

        else:
            data = {
                'result': False,
                'message': _("Forma to'liq to'ldirilmadi!"),
            }
            return JsonResponse(data=data)
    else:
        form = UpdateArticleForm(instance=article)
        context = {
            'form': form,
            'article': article,
            'review_article': ReviewerArticle.objects.filter(article=article, result=2).order_by('id'),
        }
        return render(request, "article_app/crud/update_article.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def create_article_file(request, pk):
    cwd = os.getcwd()
    article = Article.objects.get(pk=pk)
    if request.method == "POST":
        form = CreateArticleFileForm(request.POST, request.FILES)
        get_file = request.FILES.get('file', None)
        if form.is_valid() and get_file is not None:
            files = ArticleFile.objects.filter(article_id=pk)
            if files.count() > 0:
                # Warning
                article.filePDF.delete()
                for f in files:
                    f.file_status = 0
                    f.save()

            new_file = form.save(commit=False)
            new_file.save()
            article.file = new_file
            article.save()

            if is_pdf(new_file.file.path):
                article.filePDF = new_file.file
                article.save()
            else:
                out_path = f"{cwd}/media/{article.file.directory_string_var}"
                try:
                    import platform
                    plt = platform.system()

                    if plt == "Windows":
                        convert(article.file.file.path, out_path)
                    elif plt == "Linux":
                        import subprocess
                        subprocess.check_output(
                            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', out_path,
                             article.file.file.path])
                    elif plt == "Darwin":
                        import subprocess
                        args = [
                            'libreoffice',
                            '--headless',
                            '--convert-to',
                            'pdf',
                            '--outdir',
                            out_path,
                            article.file.file.path,
                        ]
                        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None)

                except Exception as e:
                    from datetime import datetime

                    now = datetime.now()

                    current_time = now.strftime("%H:%M:%S")
                    f = open('log.txt', 'w')
                    f.write('Error - %s' % e)
                    f.write(f' Time: {current_time}')
                    f.close()
                article.filePDF = f"{article.file.directory_string_var}{article.file.file_name().split('.')[0]}.pdf"
                article.save()
            data = {
                'result': True,
                'file_name': new_file.file_name(),
                'message': _('Muvaffaqiyatli amalga oshirildi!')
            }
            return JsonResponse(data=data)
        else:
            data = {
                'result': False,
                'message': _("Forma yaroqli emas!"),
            }
            return JsonResponse(data=data)
    else:
        context = {
            'form': CreateArticleFileForm(),
            'article': article,
        }
        return render(request, "article_app/crud/create_file.html", context=context)


@login_required(login_url='login')
def article_view(request, pk):
    if request.method == 'GET' and is_ajax(request=request):
        article = get_object_or_404(Article, pk=pk)
        document = None
        author = article.author
        if article.file is not None:
            ob = ArticleFile.objects.filter(
                article_id=article.id).filter(file_status=1).first()
            document = ob.file.url

        data = {
            "id": article.id,
            "author": author.full_name,
            "section": article.section.name,
            "file": f"{document}",
            "title": article.title,
            "abstract": article.abstract,
            "keywords": article.keywords,
            "article_status": article.article_status.name,
            "article_status_id": article.article_status.id,
            "is_publish": article.is_publish,
            "created_at": article.created_at.strftime("%d/%m/%Y, %H:%M:%S"),
            "updated_at": article.updated_at,
        }
        return JsonResponse(data=data)
    else:
        return redirect("dashboard")


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    objects = ArticleFile.objects.filter(article=article)

    if request.method == "POST":
        article.filePDF.delete()
        for ob in objects:
            ob.file.delete()
        article.delete()
        data = {
            "result": True,
            "message": _("Muvaffaqiyatli o'chirildi!"),
        }
        return JsonResponse(data=data)
    else:
        return render(request, 'article_app/crud/delete_article.html', {'article': article})


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def get_article_authors(request, pk):
    authors = ExtraAuthor.objects.filter(article_id=pk).order_by('id')
    lang = get_language()
    edit_url = f"/{lang}/author/edit/"
    delete_url = f"/{lang}/author/delete/"
    if lang == 'uz':
        edit_url = f"/author/edit/"
        delete_url = f"/author/delete/"

    data = {
        "authors": list(authors.values(
            'id', 'lname', 'fname', 'mname', 'email', 'work', 'scientific_degree__name'
        )),
        "edit_url": edit_url,
        "delete_url": delete_url,
    }
    return JsonResponse(data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def add_author(request, pk):
    user = request.user
    article = Article.objects.get(pk=pk)
    if user.id != article.author.id:
        return render(request, 'user_app/not_access.html')

    if request.method == 'POST':
        form = AddAuthorForm(request.POST)
        if form.is_valid():
            # if ExtraAuthor.objects.filter(article_id=pk).count() > 10:
            #     data = {'result': "limit_author",
            #             'message': _('Mualliflarni qoshish limiti 10 ta!')}
            #     return JsonResponse(data)
            form.save()
            data = {
                'result': True,
                'message': _("Muvaffaqiyatli qo'shildi!")
            }
            return JsonResponse(data)
        else:
            data = {'result': False,
                    'message': _("Xatolik yuz berdi!")}
            return JsonResponse(data)
    context = {
        'form': AddAuthorForm(),
        'user': user,
        'article': article,
    }
    return render(request, "article_app/crud/add_authors.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def edit_author(request, pk):
    author = ExtraAuthor.objects.get(pk=pk)
    article = author.article

    if request.user.id != article.author.id:
        return render(request, 'user_app/not_access.html')

    if request.method == "POST" and is_ajax(request):
        form = AddAuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            data = {
                'result': True,
                'message': _("Muvaffaqiyatli tahrirlandi!")
            }
            return JsonResponse(data)
        else:
            return JsonResponse(_("Forma to'liq emas!"))

    form = AddAuthorForm(instance=author)
    context = {
        'form': form,
        'author': author,
    }
    return render(request, "article_app/crud/edit_author.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor', 'reviewer', 'author'])
def delete_author(request, pk):
    author = ExtraAuthor.objects.get(pk=pk)
    article = author.article
    if request.user.id != article.author.id:
        return render(request, 'user_app/not_access.html')
    if request.method == "POST":
        author.delete()
        data = {
            "result": True,
            "message": _("Muvaffaqiyatli o'chirildi")
        }
        return JsonResponse(data)
    else:
        return render(request, 'article_app/crud/delete_author.html', {'author': author})


@login_required(login_url='login')
def send_message(request, pk, user_id):
    article = Article.objects.get(pk=pk)
    current_user = User.objects.get(id=request.user.id)
    author = article.author
    author_id = author.id
    roles = current_user.get_roles

    if request.method == 'GET' and is_ajax(request):
        form = SendMessageForm()
        context = {
            'form': form,
            'article': article,
            'from_user': current_user,
            'user_id': user_id,
            'roles': roles,
        }
        return render(request, 'article_app/message/send_message.html', context=context)

    elif request.method == "POST" and is_ajax(request):
        form = SendMessageForm(request.POST)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.notification_status = NotificationStatus.objects.get(pk=1)
            notif.save()
            data = {
                'result': True,
                'roles': roles,
                'message': _("Muvaffaqiyatli yuborildi!")
            }
            return JsonResponse(data)
        else:
            return JsonResponse(_("Forma to'liq emas!"))
    else:
        return HttpResponse(_("Sahifa topilmadi!"))
