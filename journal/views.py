import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from article_app.models import Article, ExtraAuthor
from fileapp.forms import CreateFileForm
from fileapp.models import TemplateFile
from journal.forms import *
from journal.models import *
from user_app.models import *
import PyPDF2
from PyPDF2 import PdfMerger
from docx import Document
from user_app.decorators import allowed_users
from django.utils.translation import gettext_lazy as _, get_language

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from django.db.models import Count
from django.contrib import messages

cwd = os.getcwd()


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def journal_years_list(request):
    objects = JournalYear.objects.all().order_by('id')
    data = {
        "objects": objects,
    }
    return render(request, "journal/journal_years.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def journal_numbers_list(request):
    objects = JournalNumber.objects.all().order_by('id')
    data = {
        "objects": objects,
    }
    return render(request, "journal/journal_numbers.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_journal_year(request):
    if request.method == "POST":
        form = JournalYearForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli qo'shildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"Xatolik yuz berdi: {form.errors}"),
            }
            return JsonResponse(data)
    data = {
        "form": JournalYearForm(),
    }
    return render(request, "journal/create_journal_year.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_journal_number(request):
    if request.method == "POST":
        form = JournalNumberForm(request.POST)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli qo'shildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"Xatolik yuz berdi: {form.errors}"),
            }
            return JsonResponse(data)
    data = {
        "form": JournalNumberForm(),
    }
    return render(request, "journal/create_journal_number.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_journal_year(request, pk):
    ob = get_object_or_404(JournalYear, pk=pk)
    if request.method == "POST":
        form = JournalYearForm(request.POST, instance=ob)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli o'zgartirildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"Xatolik yuz berdi: {form.errors}"),
            }
            return JsonResponse(data)
    data = {
        "form": JournalYearForm(instance=ob),
        "ob": ob,
    }
    return render(request, "journal/edit_journal_year.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_journal_number(request, pk):
    ob = get_object_or_404(JournalNumber, pk=pk)
    if request.method == "POST":
        form = JournalNumberForm(request.POST, instance=ob)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("Muvaffaqiyatli o'zgartirildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"Xatolik yuz berdi: {form.errors}"),
            }
            return JsonResponse(data)
    data = {
        "form": JournalNumberForm(instance=ob),
        "ob": ob,
    }
    return render(request, "journal/edit_journal_number.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_journal_year(request, pk):
    instance = get_object_or_404(JournalYear, pk=pk)
    if request.method == "POST":
        instance.delete()
        data = {
            "result": True,
            "message": _("Muvaffaqiyatli o'chirildi!"),
        }
        return JsonResponse(data)
    data = {
        "instance": instance,
    }
    return render(request, "journal/delete_journal_year.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_journal_number(request, pk):
    instance = get_object_or_404(JournalNumber, pk=pk)
    if request.method == "POST":
        instance.delete()
        data = {
            "result": True,
            "message": _("Muvaffaqiyatli o'chirildi!"),
        }
        return JsonResponse(data)
    data = {
        "instance": instance,
    }
    return render(request, "journal/delete_journal_number.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def journal_dashboard(request):
    journals = Journal.objects.all().order_by('-id')
    head_template = get_object_or_404(TemplateFile, code_name=1)
    articles = Article.objects.filter(article_status_id=2, is_publish=True, is_publish_journal=False) \
        .order_by('year', 'number', 'order_page')

    years = JournalYear.objects.filter(status=True).order_by('id')
    numbers = JournalNumber.objects.filter(status=True).order_by('id')

    data = {
        "journals": journals,
        "articles": articles,
        "head_template": head_template,
        "years": years,
        "numbers": numbers,
    }
    return render(request, "journal/journal_dashboard.html", context=data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def upload_checked_file(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST' and is_ajax(request):
        form = UploadArticleFileForm(request.POST, request.FILES)
        if form.is_valid():
            ob = form.save(commit=False)
            files = UploadFile.objects.filter(article=article)
            if files.count() > 0:
                for file in files:
                    file.file.delete()
                    file.delete()
            ob.save()
            article.is_checked_upload_file = True
            article.checked_upload_file = ob.file
            article.save()

            data = {
                "result": True,
                "message": _("Yuklash muvaffaqiyatli bajarildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Yuklashda xatolik yuz berdi!"),
            }
            return JsonResponse(data)
    context = {
        'form': UploadArticleFileForm(),
        'article': article,
    }
    return render(request, "journal/upload_checked_article_file.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def update_checked_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST' and is_ajax(request):
        form = UpdateArticleAbKeyForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": _("O'zgartirildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("O'zgartirishda xatolik yuz berdi!"),
            }
            return JsonResponse(data)
    context = {
        'form': UpdateArticleAbKeyForm(instance=article),
        'article': article,
    }
    return render(request, "journal/update_checked_article.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def select_article_orders(request):
    if request.method == "POST" and is_ajax(request):
        article_count = int(request.POST.get('article_count'))

        # for i in range(1, article_count + 1, 1):
        #     year = request.POST.get(f"select_year_{i}")
        #     number = request.POST.get(f"select_number_{i}")
        #     if year == '' or number == '':
        #         data = {
        #             "result": False,
        #             "message": _(f"{i}-maqolani yilini yoki sonini tanlamadingiz!")
        #         }
        #         return JsonResponse(data)

        for i in range(1, article_count + 1, 1):
            year = request.POST.get(f"select_year_{i}")
            number = request.POST.get(f"select_number_{i}")
            if year == '' and number == '':
                continue
            data1 = request.POST.get(f"select_year_{i}").split(',')
            data2 = request.POST.get(f"select_number_{i}").split(',')
            article_id = int(data1[0])
            year = int(data1[1])
            number = int(data2[1])
            article = get_object_or_404(Article, pk=article_id)
            article.year = year
            article.number = number
            article.save()

        # for i in range(1, article_count + 1, 1):
        #     req = request.POST.get(f"select_{i}")
        #     if req == '':
        #         data = {
        #             "result": False,
        #             "message": _(f"{i}-maqolani tartibini tanlamadingiz!")
        #         }
        #         return JsonResponse(data)

        for i in range(1, article_count + 1, 1):
            req = request.POST.get(f"select_{i}")
            if req == '':
                continue
            data = request.POST.get(f"select_{i}").split(',')
            article_id = int(data[0])
            order_number = int(data[1])
            article = get_object_or_404(Article, pk=article_id)
            article.order_page = order_number
            article.save()

    data = {
        "result": True,
        "message": _("Muvaffaqiyatli saqlandi.")
    }
    return JsonResponse(data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def create_journal(request):
    if request.method == 'POST' and is_ajax(request):
        form = CreateJournalForm(request.POST)
        year = request.POST.get('year')
        number = request.POST.get('number')

        if year == '':
            data = {
                "result": False,
                "message": _("Yilni tanlamadingiz!"),
            }
            return JsonResponse(data)
        if number == '':
            data = {
                "result": False,
                "message": _("Sonni tanlamadingiz!"),
            }
            return JsonResponse(data)
        year_j = get_object_or_404(JournalYear, pk=int(year)).year
        number_j = get_object_or_404(JournalNumber, pk=int(number)).number

        articles = Article.objects.filter(article_status_id=2, is_publish=True, is_publish_journal=False,
                                          year=int(year_j),
                                          number=int(number_j)).order_by('order_page')

        for art in articles:
            if not art.is_checked_upload_file:
                data = {
                    "result": False,
                    "message": _("Maqolalarga fayl yuklamadingiz. Yuklanmagan faylni yuklang!"),
                }
                return JsonResponse(data)

        if form.is_valid():
            journal = form.save(commit=False)
            journal.save()

            out_file = f"{cwd}/media/files/journals/mundarija/{journal.id}.docx"
            if not os.path.exists(f"{cwd}/media/files/journals/mundarija/"):
                os.makedirs(f"{cwd}/media/files/journals/mundarija/")
            doc = Document()
            doc.add_heading('Mundarija', 1)

            for article in articles:
                try:
                    JournalArticle.objects.create(
                        journal=journal,
                        article=article,
                        order_page=article.order_page,
                        year=article.year,
                        number=article.number,
                    )
                    authors = ExtraAuthor.objects.all().filter(article=article).order_by('id')
                    text: str = ""
                    for author in authors:
                        if author == authors.last():
                            text += f" {str(author.fname)[0]}.{str(author.mname)[0]}.{str(author.lname)}"
                        else:
                            text += f" {str(author.fname)[0]}.{str(author.mname)[0]}.{str(author.lname)}, "
                    doc.add_heading(f"{text}\n{article.title}", level=2)

                except Exception as e:
                    journal.delete()

                    data = {
                        "result": False,
                        "message": _(f"{e}"),
                    }
                    return JsonResponse(data)

            try:
                for article in articles:
                    authors = ExtraAuthor.objects.all().filter(article=article).order_by('id')
                    text: str = "\n"
                    for author in authors:
                        if author == authors.last():
                            text += f" {str(author.fname)[0]}.{str(author.mname)[0]}.{str(author.lname)}"
                        else:
                            text += f" {str(author.fname)[0]}.{str(author.mname)[0]}.{str(author.lname)}, "
                    doc.add_heading(f"{text}\n{article.title_en}", level=2)

                doc.save(out_file)

                journal.file_mundarija = f"files/journals/mundarija/{journal.id}.docx"
                journal.save()

            except Exception as e:
                journal.delete()
                data = {
                    "result": False,
                    "message": _(f"{e}"),
                }
                return JsonResponse(data)

            data = {
                "result": True,
                "message": _("Jurnal muvaffaqiyatli yaratildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"{form.errors}"),
            }
            return JsonResponse(data)
    context = {
        'form': CreateJournalForm(),
    }
    return render(request, "journal/create_journal.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def upload_template(request):
    if request.method == 'POST' and is_ajax(request):
        form = CreateFileForm(request.POST, request.FILES)
        if form.is_valid():
            temp = get_object_or_404(TemplateFile, code_name=0)
            ob = form.save(commit=False)
            temp.code_name = -1
            ob.code_name = 0
            ob.save()
            temp.save()
            data = {
                "result": True,
                "message": _("Yuklash muvaffaqiyatli bajarildi!"),
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _("Yuklashda xatolik yuz berdi!"),
            }
            return JsonResponse(data)
    context = {
        'form': CreateFileForm(),
    }
    return render(request, "journal/upload_template.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def edit_journal(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    if request.method == "POST" and is_ajax(request):
        form = UpdateJournalForm(request.POST, request.FILES, instance=journal)
        if not form.has_changed():
            data = {"message": _("Jurnal ma'lumotlarida o'zgarish yo'q!"), "result": False}
            return JsonResponse(data)
        if form.is_valid():
            journal_ob = form.save(commit=False)
            if journal.is_split and journal.file_pdf and journal.file_mundarija and journal.file_head_pdf and journal.status:
                journal_ob.is_publish = True
                journal_ob.save()

                data = {
                    "result": True,
                    "message": _("Muvaffaqiyatli saytga publish qilindi!")
                }
                return JsonResponse(data)
            else:
                journal_ob.is_publish = False
                journal_ob.save()

            file_pdf_head = journal.file_head_pdf.path

            reader = PyPDF2.PdfReader(file_pdf_head)
            pages_count = len(reader.pages)
            journal.count_of_head_file = pages_count

            j_articles = JournalArticle.objects.filter(journal=journal).order_by('order_page')
            s_page_number = journal.count_of_head_file

            merger1 = PdfMerger()

            for item in j_articles:
                article = get_object_or_404(Article, pk=item.article.id)

                file_pdf_ch = article.checked_upload_file.path
                merger1.append(file_pdf_ch)

                pdf = PyPDF2.PdfReader(file_pdf_ch)
                pages_count = len(pdf.pages)

                article.start_page = s_page_number + 1
                item.start_page = s_page_number + 1
                s_page_number += pages_count
                article.end_page = s_page_number
                item.end_page = s_page_number
                article.save()
                item.save()

            merger1.write(f"{cwd}/media/files/pdf_files/{journal.id}.pdf")
            merger1.close()
            journal.file_pdf = f"files/pdf_files/{journal.id}.pdf"
            journal.save()

            file_content_pdf = journal.file_pdf.path
            merger2 = PdfMerger()
            merger2.append(file_pdf_head)
            merger2.append(file_content_pdf)
            merger2.write(f"{cwd}/media/files/pdf_files/{journal.year}-{journal.number}-{journal.id}.pdf")
            merger2.close()

            if journal.file_pdf:
                journal.file_pdf.delete()
            journal.file_pdf = f"files/pdf_files/{journal.year}-{journal.number}-{journal.id}.pdf"
            journal.save()

            existing_pdf = PyPDF2.PdfReader(open(journal.file_pdf.path, "rb"))

            output = PyPDF2.PdfWriter()

            for i in range(len(existing_pdf.pages)):
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                if i == 0:
                    can.drawString(290, 30, "")
                else:
                    can.drawString(290, 30, f"{i + 1}")
                can.save()
                packet.seek(0)

                new_pdf = PyPDF2.PdfReader(packet)
                page = existing_pdf.pages[int(i)]
                page.merge_page(new_pdf.pages[0])
                output.add_page(page)

            out_file_path = f"{cwd}/media/files/journals/finish/{journal.year}-{journal.number}-{journal.id}.pdf"
            with open(out_file_path, "wb") as f:
                output.write(f)
                f.close()

            journal.file_pdf = f"files/journals/finish/{journal.year}-{journal.number}-{journal.id}.pdf"
            journal.save()

            pdf = PyPDF2.PdfReader(journal.file_pdf.path)
            j_articles = JournalArticle.objects.filter(journal=journal).order_by('order_page')
            for item in j_articles:
                newpdf = PyPDF2.PdfWriter()
                for j in range(item.article.start_page, item.article.end_page + 1, 1):
                    newpdf.add_page(pdf.pages[j - 1])

                out_path = f"{cwd}/media/files/journals/split_article/{item.article.id}.pdf"
                save_path = f"files/journals/split_article/{item.article.id}.pdf"

                with open(out_path, "wb") as out:
                    newpdf.write(out)

                if journal.is_publish:
                    item.article_pdf = save_path
                    item.article.is_publish_journal = True
                    item.article.save()
                    item.article_pdf = save_path
                    item.save()

            data = {
                "result": True,
                "message": _("Muvaffaqiyatli bajarildi!")
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": _(f"{form.errors}!")
            }
            return JsonResponse(data)

    context = {
        'form': UpdateJournalForm(instance=journal),
        'journal': journal,
    }
    return render(request, "journal/edit_journal.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def delete_journal(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    if request.method == "POST" and is_ajax(request):
        journal_articles = JournalArticle.objects.filter(journal=journal)

        if journal.file_mundarija:
            journal.file_mundarija.delete()
        if journal.file_pdf:
            file_path = f"{cwd}/media/files/pdf_files/{journal.year}-{journal.number}-{journal.id}.pdf"
            journal.file_pdf.delete()
            if os.path.exists(file_path):
                os.remove(file_path)
        if journal.file_head_pdf:
            file_path = journal.file_head_pdf.path
            journal.file_head_pdf.delete()
            if os.path.exists(file_path):
                os.remove(file_path)
        if journal.image:
            file_path = journal.image.path
            journal.image.delete()
            if os.path.exists(file_path):
                os.remove(file_path)

        for item in journal_articles:
            article = item.article
            article.is_publish_journal = False
            item.article_pdf.delete()
            article.save()
        journal.delete()
        return JsonResponse({"message": _("Muvaffaqiyatli o'chirildi!")})

    data = {"journal": journal}
    return render(request, "journal/delete_journal.html", context=data)


def journal_detail(request, pk):
    try:
        journal = get_object_or_404(Journal, pk=pk, is_publish=True)

        # select_related va prefetch_related orqali N+1 query muammosini hal qilish
        list_articles = (
            JournalArticle.objects
            .filter(journal=journal)
            .select_related('article')
            .prefetch_related('article__extraauthor_set')
            .annotate(count_author=Count('article__extraauthor'))
            .order_by('order_page')
        )

        context = {
            'journal': journal,
            'list_articles': list_articles,
            'lang': get_language(),
        }
        return render(request, "journal/journal_detail.html", context=context)
    except Exception as e:
        messages.error(request, f"Xatolik yuz berdi: {e}.")
        return redirect('journals_list')


def journals_list(request):
    objects = JournalYear.objects.filter(status=True)
    context = {
        'objects': objects,
    }
    return render(request, "journal/journals.html", context=context)


def journal_year_list(request, year):
    try:
        ob_year = get_object_or_404(JournalYear, year=int(year))
        journals = Journal.objects.filter(is_publish=True, status=True, year_id=ob_year.id).order_by('year__year',
                                                                                                     'number__number')
        return render(request, 'journal/journals_year.html', context={'journals': journals, 'year': ob_year.year})
    except Exception as e:
        messages.error(request, f"Xatolik yuz berdi. {e}.")
        return redirect('journals_list')


def journal_article_view(request, pk):
    jarticle = get_object_or_404(JournalArticle, pk=pk)
    authors = ExtraAuthor.objects.filter(article=jarticle.article)
    lang = get_language()
    return render(request, 'journal/journal_article_view.html',
                  context={'jarticle': jarticle, "authors": authors, 'lang': lang})


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def archive_journals(request):
    try:
        years = JournalYear.objects.filter(status=True).order_by('year')
    except Exception as e:
        years = JournalYear.objects.none()

    context = {
        'objects': years,
    }
    return render(request, "journal/archive_journals.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def archive_journals_numbers(request, year):
    try:
        journals = Journal.objects.filter(year__year=year, is_publish=True, status=True).order_by(
            'number__number')
        context = {
            'journals': journals,
        }
        return render(request, "journal/archive_journals_numbers.html", context=context)
    except Journal.DoesNotExist:
        context = {
            'journals': Journal.objects.none(),
        }
        return render(request, 'journal/archive_journals_numbers.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def archive_journals_articles(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    objects = JournalArticle.objects.filter(journal=journal)
    context = {
        'journal': journal,
        'objects': objects,
    }
    return render(request, "journal/archive_articles.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'editor'])
def archive_article_review(request, pk):
    article = get_object_or_404(Article, pk=pk)
    objects = ReviewerArticle.objects.filter(article=article)
    context = {
        'article': article,
        'objects': objects,
    }
    return render(request, "journal/archive_article_info.html", context=context)
