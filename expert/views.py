import os

from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _

from config import settings
from expert.functions import submit_to_moderator, compress_and_resize_jpeg
from test_maker.models import Subject, LanguageTest, SubmissionTest, StatusCheck, LevelDifficultyNational, State
from expert.forms import CheckTestExpertForm
from expert.models import Expert, CheckTestExpert, CheckedTestCount, CheckTestExpertStatus, StepTest, JobControlSheet, \
    JobControlSheetNS
from user_app.constants import check_certificate
from user_app.decorators import allowed_users
from user_app.models import User, Role
from django.db.models import Q


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


media_url = settings.MEDIA_URL
media_root = settings.MEDIA_ROOT
main_folder = "questions/"


@login_required(login_url='login')
@allowed_users(role=['expert'])
def expert_dashboard(request):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_expert:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz siz ekspertlik huquqi yo'q!")
        })
    expert = get_object_or_404(Expert, user=user)
    tests = CheckTestExpert.objects.filter(expert=expert, status_test__code__in=[2, 3], is_job_given=True,
                                           is_check=False)
    job_count = tests.count()
    context = {
        "expert_user": user,
        "job_count": job_count,
    }
    return render(request, "expert/expert_dashboard.html", context)


@login_required(login_url='login')
@allowed_users(role=['expert'])
def load_checked_jobs(request):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_expert:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz sizda ekspertlik huquqi yo'q!")
        })
    expert = get_object_or_404(Expert, user=user)
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

        objects = CheckTestExpert.objects.filter(expert=expert, status_test__code__in=[0, 1], is_job_given=True,
                                                 is_check=True).order_by('-job_given_time')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(submission_test__submission__subject__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__chapter__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__section__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__lang__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__topic__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__part__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__level_d__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__type_test_upload__name__icontains=str(search_value).lower()) |
                Q(submission_test__submission__level_dn__name__icontains=str(search_value).lower()),
                Q(status_test__name__icontains=str(search_value).lower()),
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = '-job_given_time'

        questions = objects.order_by(sort_column_name)
        questions = questions[start:limit]
        data = [item.get_data() for item in questions]
        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
def check_have_certificate(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "is_info": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    if Expert.objects.filter(user=user).exists():
        return JsonResponse(
            {"result": False, "is_info": False, "message": _("Kechirasiz siz ekspertlar ro'yxatida mavjudsiz!")})

    # check certificate from ejournal.uzbmb.uz/malaka/api-check-certificate/
    data = check_certificate(user.jshshr)

    if data['is_have_certificate'] == 1:
        if data['is_expert'] == 1:
            subject = get_object_or_404(Subject, key=data['subject'])
            subject_lang = get_object_or_404(LanguageTest, key=data['subject_lang'])
            level = get_object_or_404(LevelDifficultyNational, key=data['level'])
            data_image = data['data_img']
            is_lang_expert = False
            if subject.is_lang:
                is_lang_expert = True
            Expert.objects.create(
                user=user,
                is_expert=True,
                subject=subject,
                lang_test=subject_lang,
                level=level,
                is_have_cert=True,
                certificate_training=data_image,
                is_lang_specialist=is_lang_expert,
                is_sender=True,
            )
            role = get_object_or_404(Role, level=5)
            user.roles.add(role)
        else:
            return JsonResponse({
                "result": False,
                "is_info": True,
                "message": _("Kechirasiz sizda sertifikat bor, ammo ekspertlik huquqi yo'q!")
            })
    else:
        return JsonResponse({
            "result": False,
            "is_info": True,
            "message": _("Kechirasiz sizda sertifikat aniqlanmadi!")
        })
    data = {"result": True, "message": _("Tabriklaymiz siz expert bo'ldiz!")}
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['expert'])
def is_have_unchecked_job(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})
    expert = get_object_or_404(Expert, user=user)
    tests = CheckTestExpert.objects.filter(expert=expert, is_check=False, is_job_given=True)
    result = 0
    if tests.count() > 0:
        result = 1
    response = {
        "result": result
    }
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['expert'])
def load_test_for_expert(request):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_expert:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz siz ekspertlik huquqi yo'q!")
        })
    expert = get_object_or_404(Expert, user=user)
    jobs = CheckTestExpert.objects.filter(expert=expert, status_test__code__in=[2, 3], is_job_given=True, is_check=False)

    topic = None
    level = None
    chapter = None
    section = None

    if jobs.count() == 0:
        data = {}
        response = {
            "result": True,
            "data": data,
        }
        return JsonResponse(response)
    elif jobs.count() == 1:
        job = jobs.first()
        if job.submission_test.submission.type_test_upload.id == 1:
            if job.submission_test.submission.level_dn:
                level = job.submission_test.submission.level_dn.name
            if job.submission_test.submission.part:
                topic = job.submission_test.submission.part.name
        if job.submission_test.submission.type_test_upload.id == 2:
            if job.submission_test.submission.level_d:
                level = job.submission_test.submission.level_d.name
            if job.submission_test.submission.topic:
                topic = job.submission_test.submission.topic.name

        if job.submission_test.submission.chapter:
            chapter = job.submission_test.submission.chapter.name
        if job.submission_test.submission.section:
            section = job.submission_test.submission.section.name

        data = {
            'id': job.id,
            'submission_id': job.submission_test.id,
            'user_id': job.user.id,
            'user_fio': job.user.full_name,
            'expert_fio': job.expert.user.full_name,
            'expert_id': job.expert.id,
            'subject': job.submission_test.submission.subject.name,
            'lang': job.submission_test.submission.lang.name,
            'topic': topic,
            'chapter': chapter,
            'section': section,
            'level_d': level,
            'link_literature': job.submission_test.submission.link_literature,
            'step': job.step.name,
            'is_check': job.is_check,
            'status_test': job.status_test.name,
            'status_test_code': job.status_test.code,
            'created_at': job.created_at.strftime("%d.%m.%Y"),
            'updated_at': job.updated_at.strftime("%d.%m.%Y"),
        }
        response = {
            "result": True,
            "data": data,
        }
        return JsonResponse(response)
    else:
        return JsonResponse({
            "result": False,
            "message": _("xatolik!")
        })


@login_required(login_url='login')
@allowed_users(role=['expert'])
def check_current_test_expert(request, pk):
    user = get_object_or_404(User, pk=request.user.id)

    if user.jshshr is None:
        return JsonResponse({
            "result": False,
            "message": _("Shaxsiy ma'lumotlarizni kiriting!")
        })

    if not Expert.objects.filter(user=user).exists() and user.is_expert:
        return JsonResponse({
            "result": False,
            "message": _("Kechirasiz siz ekspertlik huquqi yo'q!")
        })

    expert = get_object_or_404(Expert, user=user)
    job = get_object_or_404(CheckTestExpert, pk=pk)

    if job.is_check:
        return JsonResponse({
            "result": False,
            "message": _("Bu ish tekshirilgan!")
        })

    if job.status_test.code == 3:
        job.status_test = get_object_or_404(CheckTestExpertStatus, code=2)
        job.step = get_object_or_404(StepTest, code=2)
        job.save()

    if request.method == "POST":
        form = CheckTestExpertForm(request.POST, instance=job)
        status = request.POST.get('status')
        message = request.POST.get('message')

        radio_rs = []
        comment_rs = []

        question = get_object_or_404(SubmissionTest, pk=job.submission_test.id)
        upload_type_id = question.submission.type_test_upload.id
        job_controls = None
        if upload_type_id == 1:
            job_controls = JobControlSheetNS.objects.filter(job=job).order_by('control_sheet_id')
        elif upload_type_id == 2:
            job_controls = JobControlSheet.objects.filter(job=job).order_by('control_sheet_id')

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

        if status == '1' and len(message) == 0:
            return JsonResponse(
                {"result": False, "message": _("Xabar yozilmadi!")})

        if status == '3' and len(message) == 0:
            return JsonResponse(
                {"result": False, "message": _("Xabar yozilmadi!")})

        # file = request.FILES.get('file', None)
        #
        # if status == '1' or status == '3':
        #     if file is None:
        #         return JsonResponse(
        #             {"result": False, "message": _("Fayl yuklanmadi!")})

        if form.is_valid():
            for it in job_controls:
                item1 = int(radio_rs[it.control_sheet.code - 1])
                item2 = comment_rs[it.control_sheet.code - 1]
                it.result = item1
                if item1 == 0:
                    it.comment = item2
                it.save()

            ob_r = form.save(commit=False)
            # if status == '1' or status == '3':
            #     number = ob_r.submission_test.test.number
            #     url = f"{main_folder}{number}/feedback"
            #     full_url = f"{media_root}{url}"
            #     tp = str(file).lower().split('.')[-1].lower()
            #
            #     if not (tp == 'docx' or tp == 'doc'):
            #         return JsonResponse(
            #             {"result": False, "message": _("MS Word fayl yuklang!")})
            #
            #     if not os.path.exists(full_url):
            #         os.makedirs(full_url)
            #
            #     fs = FileSystemStorage(location=full_url)
            #     filename = fs.save(f"{full_url}/{ob_r.expert.id}.{tp}", file)
            #     file_url = f"{url}/{filename}"
            #     ob_r.file = file_url
            ob_r.save()

            if status == '1':
                job.status_test = get_object_or_404(CheckTestExpertStatus, code=0)
                job.result = 0
                job.is_check = True
                job.save()

            if status == '2':
                job.status_test = get_object_or_404(CheckTestExpertStatus, code=1)
                job.result = 1
                job.is_check = True
                job.save()

            if status == '3':
                job.status_test = get_object_or_404(CheckTestExpertStatus, code=5)
                job.result = 2
                job.is_check = True
                job.save()

            items = CheckTestExpert.objects.filter(submission_test__id=job.submission_test.id, is_check=True)

            # Oliy Ta'lim qabuli savoli tekshiruvi
            if upload_type_id == 2:
                result_sum = 0
                results = []
                if job.job_number == 1 and job.is_check is True and question.is_check_finish is False:
                    try:
                        status_test = get_object_or_404(CheckTestExpertStatus, code=4)
                        step = get_object_or_404(StepTest, code=0)
                        CheckTestExpert.objects.create(
                            user=job.submission_test.user,
                            submission_test=question,
                            status_test=status_test,
                            step=step,
                            job_number=2
                        )
                    except Exception as e:
                        return JsonResponse({"result": False, "message": _("Xatolik yuz berdi")})

                if job.job_number == 2 and job.is_check is True and question.is_check_finish is False:
                    for item in items:
                        results.append(item.result)
                        result_sum += item.result
                    editable = 2 in results

                    if result_sum == 0 and editable is False:
                        # Dined
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=0)
                        question.is_check_finish = True
                        question.step = get_object_or_404(State, key=5)
                        question.save()

                    elif result_sum == 2 and editable is False:
                        # Confirm
                        # question.test.status = 1
                        question.status = get_object_or_404(StatusCheck, code=2)
                        question.is_check_finish = True
                        question.step = get_object_or_404(State, key=4)
                        question.save()
                        # Submit to moderator
                        submit_to_moderator(question, upload_type_id)

                    elif result_sum == 1 and editable is False:
                        # Extra expert
                        status_test = get_object_or_404(CheckTestExpertStatus, code=3)
                        step = get_object_or_404(StepTest, code=1)
                        try:
                            CheckTestExpert.objects.create(
                                user=job.submission_test.user,
                                submission_test=question,
                                status_test=status_test,
                                step=step,
                                job_number=3,
                                is_extra_expert=True,
                                # is_third_expert=True,
                            )
                        except Exception as e:
                            return JsonResponse({"result": False, "message": _("Xatolik yuz berdi")})
                        question.step = get_object_or_404(State, key=2)
                        question.save()

                    elif result_sum in [2, 3, 4] and editable is True:
                        # Qayta tahrirlash uchun
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=4)
                        question.is_check_finish = False
                        question.is_editable = True
                        question.step = get_object_or_404(State, key=3)
                        question.save()

                if job.job_number == 3 and job.is_check is True and question.is_check_finish is False:
                    if job.result == 0:
                        question.test.status = 0
                        question.step = get_object_or_404(State, key=3)
                        question.status = get_object_or_404(StatusCheck, code=0)
                        question.is_check_finish = True
                        question.save()
                    elif job.result == 1:
                        # Confirm
                        question.test.status = 1
                        question.step = get_object_or_404(State, key=3)
                        question.status = get_object_or_404(StatusCheck, code=1)
                        question.is_check_finish = True
                        question.save()
                        # Submit to moderator
                        submit_to_moderator(question, upload_type_id)
                    elif job.result == 2:
                        # Qayta tahrirlash uchun
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=4)
                        question.step = get_object_or_404(State, key=3)
                        question.is_check_finish = False
                        question.is_editable = True
                        question.save()
                    else:
                        return JsonResponse({
                            "result": False,
                            "message": _("Xatolik yuz berdi!")
                        })

                if job.job_number == 4 and job.is_check is True and job.is_extra_expert and question.is_check_finish is False:
                    if job.result == 0:
                        question.test.status = 0
                        question.step = get_object_or_404(State, key=5)
                        question.status = get_object_or_404(StatusCheck, code=0)
                        question.is_check_finish = True
                        question.save()

                    elif job.result == 1:
                        # Confirm
                        question.test.status = 1
                        question.step = get_object_or_404(State, key=3)
                        question.status = get_object_or_404(StatusCheck, code=1)
                        question.is_check_finish = True
                        question.save()
                        # Submit to moderator
                        submit_to_moderator(question, upload_type_id)
                    else:
                        return JsonResponse({
                            "result": False,
                            "message": _("Xatolik yuz berdi!")
                        })

            # Milliy sertifikat tekshiruvi
            if upload_type_id == 1:
                result_sum = 0
                results = []
                if job.job_number == 1 and job.is_check is True and question.is_check_finish is False:
                    try:
                        status_test = get_object_or_404(CheckTestExpertStatus, code=4)
                        step = get_object_or_404(StepTest, code=0)
                        CheckTestExpert.objects.create(
                            user=question.user,
                            submission_test=question,
                            status_test=status_test,
                            step=step,
                            job_number=2
                        )
                    except Exception as e:
                        return JsonResponse({"result": False, "message": _("Xatolik yuz berdi")})
                if job.job_number == 2 and job.is_check is True and question.is_check_finish is False:
                    for item in items:
                        results.append(item.result)
                        result_sum += item.result
                    editable = 2 in results
                    if result_sum == 0 and editable is False:
                        # Dined
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=0)
                        question.is_check_finish = True
                        question.step = get_object_or_404(State, key=5)
                        question.save()
                    elif result_sum == 2 and editable is False:
                        # Confirm
                        question.status = get_object_or_404(StatusCheck, code=2)
                        question.save()
                        # Submit to moderator
                        submit_to_moderator(question, upload_type_id)

                    elif result_sum == 1 and editable is False:
                        # Extra expert
                        status_test = get_object_or_404(CheckTestExpertStatus, code=3)
                        step = get_object_or_404(StepTest, code=1)
                        try:
                            CheckTestExpert.objects.create(
                                user=question.user,
                                submission_test=question,
                                status_test=status_test,
                                step=step,
                                job_number=3,
                                is_extra_expert=True
                            )
                        except Exception as e:
                            return JsonResponse({"result": False, "message": _("Xatolik yuz berdi")})
                        question.step = get_object_or_404(State, key=2)
                        question.save()
                    elif result_sum in [2, 3, 4] and editable is True:
                        # Qayta tahrirlash uchun
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=4)
                        question.is_check_finish = False
                        question.is_editable = True
                        question.step = get_object_or_404(State, key=3)
                        question.save()

                if job.job_number == 3 and job.is_check is True and question.is_check_finish is False:
                    if job.result == 0:
                        question.test.status = 0
                        question.status = get_object_or_404(StatusCheck, code=0)
                        question.is_check_finish = True
                        question.step = get_object_or_404(State, key=5)
                        question.save()
                    elif job.result == 1:
                        # Confirm
                        question.test.status = 1
                        question.status = get_object_or_404(StatusCheck, code=1)
                        question.save()
                        # Submit to moderator
                        submit_to_moderator(question, upload_type_id)
                    else:
                        return JsonResponse({
                            "result": False,
                            "message": _("Xatolik yuz berdi!")
                        })

            fan = question.submission.subject
            items = CheckedTestCount.objects.filter(expert=expert, subject=fan)

            if items.count() == 0:
                ob = CheckedTestCount.objects.create(
                    expert=expert,
                    subject=fan
                )
                ob.job_all_count = 1
                ob.save()
            elif items.count() == 1:
                item = items.first()
                i = item.job_all_count
                item.job_all_count = i + 1
                item.save()

            return JsonResponse({"result": True, "message": _("Saqlandi!")})
        else:
            return JsonResponse({"result": False, "message": _("Forma to'liq emas!")})

    form = CheckTestExpertForm(instance=job)
    test = get_object_or_404(CheckTestExpert, pk=pk)
    upload_type_id = test.submission_test.submission.type_test_upload.id
    controls = None
    if upload_type_id == 1:
        controls = JobControlSheetNS.objects.filter(job=test).order_by('id')
    elif upload_type_id == 2:
        controls = JobControlSheet.objects.filter(job=test).order_by('id')

    context = {
        "expert": expert,
        "test": test,
        "form": form,
        "controls": controls,
    }
    return render(request, "expert/checkingJobWindow.html", context)


@login_required(login_url='login')
@allowed_users(role=['expert'])
def load_checking_test_for_expert(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})

    items = Expert.objects.filter(user=user)
    if items.count() == 0:
        return HttpResponse('Not found')

    if not items.exists() and user.is_expert:
        return JsonResponse(
            {"result": False, "message": _("Kechirasiz siz ekspertlik huquqi yo'q!")})
    expert = get_object_or_404(Expert, user=user)
    tests = CheckTestExpert.objects.filter(expert=expert, status_test__code__in=[2, 4], step__code=2).order_by('-id')
    data = [test.get_data() for test in tests]

    checks = CheckedTestCount.objects.filter(expert=expert)
    count_new_test = 0
    count_denied = 0
    for it in checks:
        count_new_test += it.incoming_count
        count_denied += it.denied_count

    response = {
        "result": True,
        "data": data,
        "count_new_test": count_new_test,
        "count_denied": count_denied,
    }
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def expert_list(request):
    return render(request, "expert/experts.html")


@login_required(login_url='login')
@allowed_users(role=['admin'])
def get_experts(request):
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

        objects = Expert.objects.all().order_by('id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(subject__name__icontains=str(search_value).lower()) |
                Q(lang_test__name__icontains=str(search_value).lower()) |
                Q(level__name__icontains=str(search_value).lower()) |
                Q(is_have_cert__icontains=str(search_value).lower())
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = 'id'

        experts = objects.order_by(sort_column_name)
        experts = experts[start:limit]

        response = {
            "data": list(experts.values(
                'id', 'user__last_name', 'user__first_name', 'user__middle_name', 'subject__name', 'lang_test__name',
                'level__name', 'is_have_cert', 'is_third_expert'
            )),
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def edit_third_expert(request, pk):
    if request.method == 'GET' and is_ajax(request):
        user = get_object_or_404(User, pk=request.user.id)
        if not user.is_admin:
            data = {
                "result": 0,
                "message": "Kechirasiz siz admin emassiz!",
            }
            return JsonResponse(data)
        expert = get_object_or_404(Expert, pk=pk)
        if expert.is_third_expert:
            expert.is_third_expert = False
        elif not expert.is_third_expert:
            expert.is_third_expert = True

        expert.save()
        data = {
            "result": 1,
            "message": "Muvaffaqiyatli o'zgartirildi",
        }
        return JsonResponse(data)


@login_required(login_url='login')
@allowed_users(role=['expert'])
def upload_certificate(request):
    user = get_object_or_404(User, pk=request.user.id)
    main_folder1 = "certificates/"
    if request.method == 'POST' and is_ajax(request) and request.FILES.get('image_cer'):
        image = request.FILES['image_cer']
        output_folder = f"{media_root}{main_folder1}"
        expert = get_object_or_404(Expert, user=user)
        expert.certificate_assessment = image
        expert.save()
        file_name = str(expert.certificate_assessment.name).split('/')[-1]
        compress_and_resize_jpeg(expert.certificate_assessment.path, os.path.join(output_folder, file_name), quality=85,
                                 width=720, height=1152)
        data = {
            "result": 1,
            "message": "ok"
        }
        return JsonResponse(data)
    else:
        data = {
            "result": 0,
            "message": "Xatolik yuz berdi"
        }
        return JsonResponse(data)
