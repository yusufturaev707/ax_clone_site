import os
import platform

import numpy as np

from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from admin1.models import TypeVoice, AudioLanguage
from config import settings
from expert.models import ExpertiseQuestionJob
from moderator.forms import TexTestForm, TestImageForm, AnswerTestFillForm, CheckJobModeratorForm
from moderator.models import *
from question.models import Status as QuestionStatus, QuestionNational, MockQuestion
from question.models import QuestionAdmission
from test_maker.models import TestImage, TypeTest, SubjectBox, Teacher, QuestionBox, State, TestConfirmationCount, \
    StatusCheck
from user_app.decorators import allowed_users
from user_app.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

media_url = settings.MEDIA_URL
media_root = settings.MEDIA_ROOT
main_folder = "questions/"


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def moderator_dashboard(request):
    user = get_object_or_404(User, pk=request.user.id)
    moderator = get_object_or_404(Moderator, user=user)
    tests = ModeratorCheckTest.objects.filter(moderator=moderator, result=0, is_job_given=True)
    job_count = tests.count()
    context = {
        "moderator": moderator,
        "job_count": job_count,
    }
    return render(request, "moderator/moderator_dashboard.html", context)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def load_test_moderator(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    if not user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz sizda moderator roli mavjud emas!")
        })
    moderator = get_object_or_404(Moderator, user=user)
    upload_type = moderator.upload_type
    tests = ModeratorCheckTest.objects.filter(moderator=moderator, status__key=2, is_job_given=1,
                                              upload_type=upload_type).order_by('id')

    topic = None
    level = None
    chapter = None
    section = None
    part = None

    if tests.count() == 0:
        data = {}
        response = {
            "result": True,
            "data": data,
        }
        return JsonResponse(response)
    elif tests.count() == 1:
        job = tests.first()

        if upload_type.id == 2:
            if job.submission_test.submission.level_d:
                level = job.submission_test.submission.level_d.name
            if job.submission_test.submission.topic:
                topic = job.submission_test.submission.topic.name
            if job.submission_test.submission.chapter:
                chapter = job.submission_test.submission.chapter.name
            if job.submission_test.submission.section:
                section = job.submission_test.submission.section.name
        elif upload_type.id == 1:
            if job.submission_test.submission.level_dn:
                level = job.submission_test.submission.level_dn.name
            if job.submission_test.submission.part:
                part = job.submission_test.submission.part.name

        data = {
            'id': job.id,
            'submission_id': job.submission_test.id,
            'moderator_fio': job.moderator.user.full_name,
            'subject': job.submission_test.submission.subject.name,
            'lang': job.submission_test.submission.lang.name,
            'topic': topic,
            'chapter': chapter,
            'section': section,
            'level': level,
            'part': part,
            'status': job.status.name,
            'job_given_time': job.created_at.strftime("%d.%m.%Y"),
        }
        response = {
            "result": True,
            "data": data,
        }
        return JsonResponse(response)
    else:
        print("Xatolik url: moderator/views.py/load_test_for_moderator")


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def pass_saving(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_full_personal_data:
        return JsonResponse({
            "result": False,
            "message": _("Shaxsiy ma'lumotlarizni kiriting!")
        })

    if not Moderator.objects.filter(user=user).exists() and user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz siz moderatorlik huquqi yo'q!")
        })

    test = get_object_or_404(ModeratorCheckTest, pk=pk)

    if request.method == "POST" and is_ajax(request):
        if request.POST.get('tex_code') == '':
            return JsonResponse({"result": False, "message": _("Tex code is required!")})
        form = TexTestForm(request.POST, instance=test.submission_test.test)

        images = request.FILES.getlist('images')

        if len(images) > 0:
            test.submission_test.is_have_img = True
            test.submission_test.save()

        if len(images) == 0:
            test.submission_test.is_have_img = False
            test.submission_test.save()

        is_all_img = True

        for img in images:
            tp = str(img).lower().split('.')[-1]

            if tp == 'jpg' or tp == 'jpeg' or tp == 'png':
                continue
            else:
                is_all_img = False

        if not is_all_img:
            return JsonResponse({"result": False, "message": _("Kechirasiz siz faqat rasm fayllarini yuklay olasiz!")})

        if form.is_valid():
            f = form.save()
            tex_code = f.tex_code

            url = f"{main_folder}{f.number}/tex"
            full_url_tex = f"{media_root}{url}"

            if not os.path.exists(full_url_tex):
                os.makedirs(full_url_tex)

            with open(f"{full_url_tex}/{f.number}.tex", 'w', encoding="utf-8") as file:
                file.write(tex_code)

            from subprocess import check_output

            url = f"{main_folder}{f.number}/pdf"
            full_url_pdf = f"{media_root}{url}"

            if not os.path.exists(full_url_pdf):
                os.makedirs(full_url_pdf)

            command = f"pdflatex -output-directory {full_url_pdf}"
            tex_file = f"{full_url_tex}/{f.number}.tex"

            plt = platform.system()

            if plt == "Windows":
                check_output(f"{command} {tex_file}", shell=True)
            elif plt == "Linux":
                os.system(command=f"{command} {tex_file}")

            for img in images:
                tp = str(img).lower().split('.')[-1]

                number = f.number
                url = f"{main_folder}{number}/images"
                full_url = f"{media_root}{url}"
                if not os.path.exists(full_url):
                    os.makedirs(full_url)

                f_path = f"{full_url}/{img}"
                file_url = f"{url}/{img}"

                with open(f"{f_path}", "wb+") as destination:
                    for chunk in img.chunks():
                        destination.write(chunk)

                # if os.path.exists(f_path):
                #     os.remove(f_path)

                TestImage.objects.create(
                    user=user,
                    test=f,
                    img=file_url,
                    number=number,
                )

            a = request.POST.get('a')
            b = request.POST.get('b')
            c = request.POST.get('c')
            d = request.POST.get('d')

            if len(a) == 0 or len(b) == 0 or len(c) == 0 or len(d) == 0:
                return JsonResponse(
                    {"result": False, "message": _("Kechirasiz yopiq test variantlarini to'liq kiritmadingiz!")})

            test = get_object_or_404(ModeratorCheckTest, pk=pk)

            if test.submission_test.test_type is not None:
                if test.submission_test.test_type.code != 0:
                    return JsonResponse(
                        {"result": False,
                         "message": _("Kechirasiz, Siz bu test turini yopiq test deb belgiladingiz!")})

            test.submission_test.a = a
            test.submission_test.b = b
            test.submission_test.c = c
            test.submission_test.d = d
            test.submission_test.test_type = get_object_or_404(TypeTest, code=0)
            test.submission_test.save()

            return JsonResponse({
                "result": True,
                "message": _("Muvaffaqiyatli bajarildi!")
            })
        else:
            return JsonResponse({
                "result": False,
                "message": _("Forma validmas!")
            })
    else:
        return JsonResponse({
            "result": False,
            "message": _("Post requestmas!")
        })


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def convert_to_tex(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_full_personal_data:
        return JsonResponse({
            "result": False,
            "message": _("Shaxsiy ma'lumotlarizni kiriting!")
        })

    if not Moderator.objects.filter(user=user).exists() and user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz siz moderatorlik huquqi yo'q!")
        })

    test = get_object_or_404(ModeratorCheckTest, pk=pk)

    if test.status.key == 1 and test.result == 1:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz bu savol texga o'tkazilgan!")
        })

    if request.method == "POST" and is_ajax(request):
        test = get_object_or_404(ModeratorCheckTest, pk=pk)
        test.status = get_object_or_404(Status, key=1)
        test.result = 1
        ctc = get_object_or_404(ConvertTexCount, moderator=test.moderator)
        ctc.converted_count += 1
        test.save()
        ctc.save()

        test.submission_test.step = get_object_or_404(State, key=5)
        test.submission_test.is_check_finish = True
        test.submission_test.save()

        try:
            test = get_object_or_404(ModeratorCheckTest, pk=pk)
            qa = QuestionAdmission.objects.create(
                number=test.submission_test.test.number,
                submission_test=test.submission_test,
                user=test.user,
                subject=test.submission_test.submission.subject,
                language=test.submission_test.submission.lang,
                theme=test.submission_test.submission.topic,
                level=test.submission_test.submission.level_d,
                tex_code=test.submission_test.test.tex_code,
                a=test.submission_test.a,
                b=test.submission_test.b,
                c=test.submission_test.c,
                d=test.submission_test.d,
                status=get_object_or_404(QuestionStatus, key=1)
            )

            subject_boxs = SubjectBox.objects.filter(teacher__user_id=qa.user.id, subject=qa.subject, lang=qa.language)
            teacher = get_object_or_404(Teacher, user=test.user)

            # Birinchi marta yaratishdagi jarayon
            if subject_boxs.count() == 0:
                sb = SubjectBox.objects.create(
                    teacher=teacher,
                    subject=qa.subject,
                    lang=qa.language,
                    count=1
                )
                qb_count = QuestionBox.objects.filter(subject_box=sb).count()
                if qb_count == 0:
                    qb = QuestionBox.objects.create(
                        subject_box=sb,
                        box_number=101,
                        count_question=1,
                        limit_question=sb.subject.limit_question,
                    )
                    qb.questions.add(qa)

            # Qolgan holatdagi jarayon
            elif subject_boxs.count() == 1:
                subject_box = get_object_or_404(SubjectBox, teacher=teacher, subject=qa.subject, lang=qa.language)
                i = subject_box.count
                subject_box.count = i + 1
                subject_box.save()

                ob_box = QuestionBox.objects.filter(subject_box=subject_box).last()
                count_question = ob_box.count_question
                limit = ob_box.limit_question

                if 0 < count_question < limit:
                    ob_box.count_question = count_question + 1
                    ob_box.save()
                    ob_box.questions.add(qa)

                elif count_question == limit:
                    box_number = ob_box.box_number
                    qb = QuestionBox.objects.create(
                        subject_box=subject_box,
                        box_number=box_number + 1,
                        count_question=1,
                        limit_question=subject_box.subject.limit_question,
                    )
                    qb.questions.add(qa)

            else:
                print("Xatolik yuz berdi")
            print("Yaratildi")

        except Exception as e:
            return JsonResponse({
                "message": _(f"Savol yaratishda xatolik yuz berdi: {e}")
            })

        return JsonResponse({
            "result": True,
            "message": _("Muvaffaqiyatli bajarildi!")
        })

    form = TexTestForm(instance=test.submission_test.test)
    img_form = TestImageForm()
    answer_form = AnswerTestFillForm(instance=test.submission_test)

    url = f"{main_folder}{test.submission_test.test.number}/pdf"
    full_url_pdf = f"{media_url}{url}/{test.submission_test.test.number}.pdf"

    images = TestImage.objects.filter(test=test.submission_test.test)

    base_url = request._current_scheme_host

    context = {
        "moderator": test.moderator,
        "test": test,
        "form": form,
        "img_form": img_form,
        "answer_form": answer_form,
        "full_url_pdf": full_url_pdf,
        "images": images,
        "base_url": base_url,
    }
    return render(request, "moderator/convertTexModerator.html", context)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def view_image_path(request, pk):
    image = get_object_or_404(TestImage, pk=pk)
    context = {
        "image_path": image.img.path
    }
    return render(request, "moderator/view_img_url.html", context)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def delete_image(request, pk):
    image = get_object_or_404(TestImage, pk=pk)
    if os.path.exists(image.img.path):
        os.remove(image.img.path)
    image.delete()
    return JsonResponse({"result": True})


@login_required(login_url='login')
@allowed_users(role=['admin'])
def moderator_list(request):
    return render(request, "moderator/moderators.html")


@login_required(login_url='login')
@allowed_users(role=['admin'])
def get_moderators(request):
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        limit = start + length

        objects = Moderator.objects.all().order_by('id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(id__icontains=str(search_value).lower())
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = 'id'

        moderators = objects.order_by(sort_column_name)
        moderators = moderators[start:limit]

        response = {
            "data": list(moderators.values(
                'id', 'user__last_name', 'user__first_name', 'user__middle_name', 'is_moderator'
            )),
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def get_work_for_moderator(request):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_moderator:
        data = {
            "result": 0,
            "message": "Kechirasiz siz moderator emassiz!",
        }
        return JsonResponse(data=data)
    moderator = get_object_or_404(Moderator, user=user)

    if moderator.is_moderator is False:
        data = {
            "result": 0,
            "message": "Kechirasiz sizda to'liq moderator roli mavjud emas!",
        }
        return JsonResponse(data=data)

    upload_type = moderator.upload_type

    items = ModeratorCheckTest.objects.filter(moderator=moderator, upload_type=upload_type, status__key=2,
                                              is_job_given=1)  # tugallanmagan ish bor yo'qligi
    moderator_subject = None
    moderator_lang = None
    if upload_type.id == 1:
        moderator_subject = moderator.subject
        moderator_lang = moderator.language

        items = items.filter(submission_test__submission__subject=moderator_subject, submission_test__submission__lang=moderator_lang)

    if items.count() > 0:
        data = {
            "result": 0,
            "message": "Ayni vaqta sizda tekshirilmagan ish mavjud!",
        }
        return JsonResponse(data=data)

    with atomic():
        objects = ModeratorCheckTest.objects.filter(is_job_given=0, status__key=2, upload_type=upload_type).exclude(
            user=user).order_by('id')
        if upload_type.id == 1:
            objects = objects.filter(submission_test__submission__subject=moderator_subject, submission_test__submission__lang=moderator_lang)

        if objects.count() == 0:
            data = {
                "result": 0,
                "message": f"Ayni vaqta tizimda ish topilmadi!!",
            }
            return JsonResponse(data=data)

        works_id = [item.id for item in objects]
        select_random_id = np.random.choice(works_id, 1, replace=False).tolist()
        work = get_object_or_404(ModeratorCheckTest, pk=int(select_random_id[0]))

        work.moderator = moderator
        work.is_job_given = 1
        work.job_given_time = timezone.now()
        work.save()

        if not ConvertTexCount.objects.filter(moderator=moderator).exists():
            ConvertTexCount.objects.create(
                moderator=moderator,
            )

        data = {
            "result": 1,
            "message": f"Ok",
        }
        return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def check_status(request):
    pass


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def check_status_id(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    if not user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz sizda moderator roli mavjud emas!")
        })
    try:
        job = get_object_or_404(ModeratorCheckTest, pk=pk)
    except Exception as e:
        return JsonResponse({
            "result": False,
            "message": _("Ish topilmadi!")
        })

    data = {
        'id': job.id,
    }
    response = {
        "result": True,
        "data": data,
    }
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def checking_job(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    if not user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz sizda moderator roli mavjud emas!")
        })
    try:
        job_id = request.GET.get('jobId')
        job = get_object_or_404(ModeratorCheckTest, pk=int(job_id))
    except Exception as e:
        return JsonResponse({
            "result": False,
            "message": _("Ish topilmadi!")
        })

    data = {
        'id': job.id,
    }
    response = {
        "result": True,
        "data": data,
    }
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['moderator'])
def checking_job_window(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    if not user.is_moderator:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz sizda moderator roli mavjud emas!")
        })
    moderator = get_object_or_404(Moderator, user=user)
    try:
        job = get_object_or_404(ModeratorCheckTest, pk=pk)
    except Exception as e:
        return JsonResponse({
            "result": False,
            "message": _("Ish topilmadi!")
        })

    if request.method == "POST" and is_ajax(request):
        form = CheckJobModeratorForm(request.POST, instance=job)
        status = request.POST.get('status')

        if job.submission_test.submission.part.key == 'l':
            type_voice = request.POST.get('type_voice', None)
            text_string = request.POST.get('text_string', None)

            if type_voice == '' or text_string == '':
                return JsonResponse(
                    {"result": False, "message": "Voice turi tanlanmadi yoki matn maydoni to'ldirilmadi"})

        radio_rs = []
        comment_rs = []
        job_controls = ExpertiseQuestionJob.objects.filter(job=job).order_by('control_sheet_id')
        for item in job_controls:
            code = item.control_sheet.code
            r = f"res_radio{code}"
            cm = f"comment{code}"
            rs = request.POST.get(r, None)
            rcm = request.POST.get(cm)
            radio_rs.append(rs)
            comment_rs.append(rcm)

        n = job_controls.count()
        for i in range(n):
            if radio_rs[i] is None:
                return JsonResponse(
                    {"result": False, "message": _("Nazorat savollariga to'liq javob bermadingiz!")})
            continue

        for i in range(n):
            if radio_rs[i] == '0' and comment_rs[i] == '':
                return JsonResponse(
                    {"result": False, "message": _("Nazorat savollariga izoh yozmadingiz!")})
            continue

        if status == '':
            return JsonResponse(
                {"result": False, "message": _("Tasdiq holatini tanlamadingiz!")})

        if form.is_valid():
            for it in job_controls:
                item1 = int(radio_rs[it.control_sheet.code - 1])
                item2 = comment_rs[it.control_sheet.code - 1]
                it.result = item1
                if item1 == 0:
                    it.comment = item2
                it.save()

            job.job_finish_time = timezone.now()
            job.result = int(status)
            job.is_check = True
            job.save()
            form.save()

            job = get_object_or_404(ModeratorCheckTest, pk=job.id)
            subject = job.submission_test.submission.subject
            part_option = job.submission_test.submission.part_option
            submission_user = job.submission_test.submission.user
            file_word = job.submission_test.test.file_word
            question_number = job.submission_test.test.number

            objects = CheckedTest.objects.filter(moderator=moderator, subject=subject)
            if objects.count() == 0:
                CheckedTest.objects.create(
                    moderator=moderator,
                    subject=subject,
                    converted_count=1
                )
            elif objects.count() > 0:
                ob = get_object_or_404(CheckedTest, moderator=moderator, subject=subject)
                n = ob.converted_count
                ob.converted_count = n + 1
                ob.save()

            job.submission_test.step = get_object_or_404(State, key=5)
            job.submission_test.is_check_finish = True

            if job.status.key == 1:
                try:
                    QuestionNational.objects.create(
                        number=question_number,
                        submission_test=job.submission_test,
                        user=submission_user,
                        subject=subject,
                        language=job.submission_test.submission.lang,
                        part=job.submission_test.submission.part,
                        level=job.submission_test.submission.level_dn,
                        part_option=part_option,
                        file_word=file_word,
                        status=get_object_or_404(QuestionStatus, key=1),
                    )
                    job.submission_test.status = get_object_or_404(StatusCheck, code=1)
                    job.submission_test.save()
                except Exception as e:
                    return JsonResponse({"result": False, "message": _(f"{e}")})

                objects = TestConfirmationCount.objects.filter(user=job.user, subject=subject, level=job.submission_test.submission.level_dn, section=job.submission_test.submission.part, part=job.submission_test.submission.part_option)
                if objects.count() == 0:
                    try:
                        TestConfirmationCount.objects.create(
                            user=submission_user,
                            subject=subject,
                            subject_lang=job.submission_test.submission.lang,
                            level=job.submission_test.submission.level_dn,
                            section=job.submission_test.submission.part,
                            part=part_option,
                            count=1,
                        )
                    except Exception as e:
                        return JsonResponse({"result": False, "message": f"{e}"})
                elif objects.count() > 0:
                    ob_test = get_object_or_404(TestConfirmationCount, user=job.user, subject=subject, level=job.submission_test.submission.level_dn, section=job.submission_test.submission.part, part=job.submission_test.submission.part_option)
                    i = ob_test.count
                    ob_test.count = i + 1
                    ob_test.save()

                return JsonResponse({"result": True, "message": _("Muvaffaqiyatli bazaga yozildi!")})
            elif job.status.key == 0:
                job.submission_test.status = get_object_or_404(StatusCheck, code=0)
                job.submission_test.save()
                return JsonResponse({"result": True, "message": _("Bu savol bazaga yozilmadi!")})

    controls = ExpertiseQuestionJob.objects.filter(job=job).order_by('id')
    form = CheckJobModeratorForm(instance=job)

    type_voices = TypeVoice.objects.all().order_by('id')
    languages = AudioLanguage.objects.all()

    context = {
        "moderator": moderator,
        "job": job,
        "controls": controls,
        "form": form,
        "type_voices": type_voices,
        "languages": languages,
    }
    return render(request, "moderator/checkingJobWindow.html", context)
