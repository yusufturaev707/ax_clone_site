import json
import os.path

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language
from django.core.files.storage import FileSystemStorage

from moderator.models import ModeratorCheckTest, Moderator
from test_maker.models import *
from expert.models import Expert, StepTest, CheckTestExpertStatus, CheckTestExpert, CheckedTestCount, JobControlSheet, \
    ControlSheet, Sheet, ControlSheetNS, JobControlSheetNS, Status, ExpertiseQuestionJob
from user_app.decorators import allowed_users
from user_app.models import User
from test_maker.forms import *
import numpy as np
from django.utils._os import safe_join


# BASE_DIR = '/home/user/project/media/questions/'
# BASE_DIR = 'C:/Django/axborotnomadtm/media/questions/'

media_url = settings.MEDIA_URL
media_root = settings.MEDIA_ROOT
main_folder = "questions/documents/"


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['admin'])
def get_subjects(request):
    subjects = Subject.objects.all().order_by('id')
    context = {
        "subjects": subjects
    }
    return render(request, "test_maker/subjects.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def create_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        s_name = request.POST.get('name')
        key = request.POST.get('key')
        duration = request.POST.get('duration')
        limit_question = request.POST.get('limit_question')

        if s_name == '' or key == '' or duration == '' or limit_question == '':
            data = {
                "result": False,
                "message": "Malumotlar to'liq emas!",
                "error": form.errors,
            }
            return JsonResponse(data)

        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": "Yaratildi",
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": "Malumotlarni to'ldirishda xatolik yuz berdi",
                "error": form.errors,
            }
            return JsonResponse(data)

    form = SubjectForm()
    context = {
        "form": form
    }
    return render(request, "test_maker/create_subject.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        s_name = request.POST.get('name')
        key = request.POST.get('key')
        duration = request.POST.get('duration')
        limit_question = request.POST.get('limit_question')

        if s_name == '' or key == '' or duration == '' or limit_question == '':
            data = {
                "result": False,
                "message": "Malumotlar to'liq emas!",
                "error": form.errors,
            }
            return JsonResponse(data)

        if form.is_valid():
            form.save()
            data = {
                "result": True,
                "message": "Yaratildi",
            }
            return JsonResponse(data)
        else:
            data = {
                "result": False,
                "message": "Malumotlarni to'ldirishda xatolik yuz berdi",
                "error": form.errors,
            }
            return JsonResponse(data)

    form = SubjectForm(instance=subject)
    context = {
        "form": form,
        "subject": subject,
    }
    return render(request, "test_maker/edit_subject.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        data = {
            "message": "O'chirildi",
        }
        return JsonResponse(data)
    context = {
        "subject": subject,
    }
    return render(request, "test_maker/delete_subject.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['out_expert'])
def get_subject_by_typeid(request):
    type_upload_id = request.GET.get('type_id')
    subjects = Subject.objects.filter(status=True)
    if int(type_upload_id) == 1:
        subjects = subjects.filter(is_lang=True)
    data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert'])
def get_topic_by_section(request):
    section_id = request.GET.get('section_id')
    topics = Theme.objects.filter(section_id=section_id)
    data = [{'id': topic.id, 'name': topic.name} for topic in topics]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert'])
def get_chapter_by_subject(request):
    subject_id = request.GET.get('subject_id')
    chapters = Chapter.objects.filter(subject__id=subject_id)
    data = [{'id': item.id, 'name': item.name} for item in chapters]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert'])
def get_section_by_chapter(request):
    chapter_id = request.GET.get('chapter_id')
    sections = Section.objects.filter(chapter_id=chapter_id)
    data = [{'id': item.id, 'name': item.name} for item in sections]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_lang_by_subject(request):
    subject_id = request.GET.get('subject_id')
    subject = get_object_or_404(Subject, pk=int(subject_id))
    languages = LanguageTest.objects.all().order_by('id')
    data = []
    if subject.is_lang:
        language = get_object_or_404(LanguageTest, key=subject.lang_key)
        data.append({'id': language.id, 'name': language.name})
    else:
        data = [{'id': language.id, 'name': language.name} for language in languages]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_part_by_type(request):
    upload_type_id = request.GET.get('upload_type_id')
    subject_id = request.GET.get('subject_id')
    subject = get_object_or_404(Subject, pk=int(subject_id))
    parts = Part.objects.filter(status=True)
    if int(upload_type_id) == 1 and subject.is_lang:
        parts = parts.filter(is_lang=True)
    elif not (int(upload_type_id) == 1 and subject.is_lang):
        parts = parts.filter(is_lang=False)
    data = [{'id': part.id, 'name': part.name} for part in parts]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_is_have_audio(request):
    subject_id = request.GET.get('subject_id')
    part_id = request.GET.get('part_id')
    subject = get_object_or_404(Subject, pk=int(subject_id))
    part = get_object_or_404(Part, pk=int(part_id), subject=subject)
    is_have_audio = False
    if part.key == 'l' or part.key == 's':
        is_have_audio = True
    data = {
        "is_have_audio": is_have_audio
    }
    return JsonResponse(data)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def upload_test(request):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_full_personal_data:
        return JsonResponse(
            {"result": False, "message": _("Test yuborishdan oldin shaxsiy ma'lumotlaringizni to'ldiring!")})

    if request.method == "POST" and is_ajax(request):
        if not user.is_expert:
            return JsonResponse(
                {"result": False, "message": _("Ruxsat mavjud emas. Sizda sertifikat aniqlanmadi")})
        form = SubmissionForm(request.POST)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = user
            submission.save()

            if submission.type_test_upload.id == 1:
                submission.type_test = get_object_or_404(TypeTest, code=1)

            if submission.type_test_upload.id == 2:
                submission.type_test = get_object_or_404(TypeTest, code=0)

            submission.save()
            subject_id = submission.subject.id
            subject_lang_id = submission.lang.id

            expert = get_object_or_404(Expert, user=user)
            if expert.subject.id != subject_id:
                submission.delete()
                return JsonResponse(
                    {"result": False, "message": _(f"{expert.subject.name} fanidan test savoli yuklay olasiz!")})
            elif expert.subject.id == subject_id and expert.lang_test.id != subject_lang_id:
                submission.delete()
                return JsonResponse(
                    {"result": False, "message": _(
                        f"{expert.subject.name} fanidan {expert.lang_test.name} dagi test savoli yuklay olasiz!")})

            lang = get_language()
            url = f"/{lang}/test_maker/upload_test/{submission.id}/"
            if lang == 'uz':
                url = f"/test_maker/upload_test/{submission.id}/"
            return JsonResponse(
                {"result": True, "url": url})
        else:
            return JsonResponse({"result": False, "message": _("Forma to'liq emas!")})
    context = {
        "type_uploads": TypeTestUpload.objects.filter(status=True),
        'languages': LanguageTest.objects.all().order_by('id'),
    }
    return render(request, "test_maker/upload_test.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def edit_test(request, pk):
    user = get_object_or_404(User, pk=request.user.id)

    if not user.is_full_personal_data:
        return JsonResponse({"result": False,
                             "message": _("Test yuborishdan oldin shaxsiy ma'lumotlaringizni to'ldiring!")})

    if not user.is_expert:
        return JsonResponse(
            {"result": False, "message": _("Ruxsat mavjud emas. Sertifikat aniqlanmadi")})

    submission = get_object_or_404(Submission, pk=pk)
    if request.method == "POST" and is_ajax(request):
        form = EditSubmissionForm(request.POST, instance=submission)

        files = request.FILES.getlist('file_word')
        topic = request.POST.get('topic')
        topic_n = request.POST.get('topic_n')
        chapter = request.POST.get('chapter')
        section = request.POST.get('section')
        part = request.POST.get('part')
        level_d = request.POST.get('level_d')
        level_dn = request.POST.get('level_dn')
        part_option = request.POST.get('part_option')

        if submission.type_test_upload.id == 1:
            if part == '':
                return JsonResponse({"result": False, "message": _("Bo'limni kiriting!")})
            if level_dn == '':
                return JsonResponse({"result": False, "message": _("Iltimos qiyinlik darajani tanlang!")})
            if part_option == '':
                return JsonResponse({"result": False, "message": _("Iltimos qismni tanlang!")})
            if topic_n == '':
                return JsonResponse({"result": False, "message": _("Iltimos mavzuni kiriting!")})
        elif submission.type_test_upload.id == 2:
            if chapter == '':
                return JsonResponse({"result": False, "message": _("Bobni kiriting!")})
            if section == '':
                return JsonResponse({"result": False, "message": _("Bo'limni kiriting!")})
            if topic == '':
                return JsonResponse({"result": False, "message": _("Mavzuni kiriting!")})
            if level_d == '':
                return JsonResponse({"result": False, "message": _("Iltimos qiyinlik darajani tanlang!")})

        if len(files) == 0:
            return JsonResponse({"result": False, "message": _("Iltimos faylni yuklang!")})

        array_word = []
        for f in files:
            tp = str(f).lower().split('.')[-1].lower()
            array_word.append(tp)

        is_docx = False
        is_doc = False

        if 'docx' in array_word:
            is_docx = True

        if 'doc' in array_word:
            is_doc = True

        if not (is_docx or is_doc):
            return JsonResponse({"result": False, "message": _("Iltimos word fayl yuklang!")})

        # if len(link_literature) == 0:
        #     return JsonResponse({"result": False, "message": _("Qaysi qismga tegishliligini yozing!")})

        if submission.type_test_upload.id == 1:
            if len(files) > 1:
                return JsonResponse({"result": False, "message": _("Iltimos faqat 1 ta word fayl yuklang!")})

        if form.is_valid():
            form.save()

            submission = get_object_or_404(Submission, pk=pk)
            for f in files:
                tp = str(f).lower().split('.')[-1]

                if tp == 'doc' or tp == 'docx':
                    st = SubmissionTest.objects.create(
                        user=user,
                        submission=submission,
                        status=get_object_or_404(StatusCheck, code=2),
                    )
                    number = str(st.id).zfill(8)
                    url = f"{main_folder}{number}"  # Path relative to media root
                    full_url = os.path.join(media_root, url)

                    if not os.path.exists(full_url):
                        os.makedirs(full_url)

                    fs = FileSystemStorage(location=full_url)
                    filename = f"{number}.{tp}"

                    saved_filename = fs.save(filename, f)
                    file_url = os.path.join(url, saved_filename)

                    test = Test.objects.create(
                        user=user,
                        file_word=file_url,
                        number=number,
                    )

                    SubmissionTest.objects.filter(pk=st.id).update(
                        user=user,
                        submission=submission,
                        test=test,
                        step=get_object_or_404(State, key=1),
                    )

            submissions = SubmissionTest.objects.filter(user=user, submission=submission).order_by('id')

            for ob in submissions:
                status_test = get_object_or_404(CheckTestExpertStatus, code=4)
                step = get_object_or_404(StepTest, code=0)

                try:
                    CheckTestExpert.objects.create(
                        user=user,
                        submission_test=ob,
                        status_test=status_test,
                        step=step,
                    )
                except Exception as e:
                    return JsonResponse({"result": False, "message": _("Xatolik yuz berdi")})

            lang = get_language()
            url = f"/{lang}/test_maker/my_submit_tests/"
            if lang == 'uz':
                url = f"/test_maker/my_submit_tests/"
            return JsonResponse(
                {"result": True, "url": url, "message": _("Muvaffaqiyatli yuborildi!")})
        else:
            return JsonResponse({"result": False, "message": _("Forma to'liq emas!")})
    levels = None
    if submission.type_test_upload.id == 1:
        levels = LevelDifficultyNational.objects.all().order_by('-id')
    elif submission.type_test_upload.id == 2:
        levels = LevelDifficulty.objects.all().order_by('id')

    context = {
        "form": EditSubmissionForm(instance=submission),
        'fileForm': TestForm(),
        'submission': submission,
        'levels': levels,
        'subjects': Subject.objects.all().order_by('id'),
        'test_types': TypeTestUpload.objects.all().order_by('-id'),
    }
    return render(request, "test_maker/upload_test_form.html",
                  context=context)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def resend_test(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    if not user.is_full_personal_data:
        return JsonResponse({"result": False,
                             "message": _("Test yuborishdan oldin shaxsiy ma'lumotlaringizni to'ldiring!")})
    if not user.is_expert:
        return JsonResponse(
            {"result": False, "message": _("Ruxsat mavjud emas. Sertifikat aniqlanmadi")})
    question = get_object_or_404(SubmissionTest, pk=pk)
    if not question.is_editable:
        return JsonResponse(
            {"result": False, "message": _("Xatolik yuz berdi")})

    if request.method == "POST" and is_ajax(request):
        files = request.FILES.getlist('file_word')
        topic_n = request.POST.get('topic_n')

        if topic_n == '':
            return JsonResponse({"result": False, "message": _("Iltimos mavzuni kiriting!")})

        if len(files) == 0:
            return JsonResponse({"result": False, "message": _("Iltimos faylni yuklang!")})

        array_word = []
        for f in files:
            tp = str(f).lower().split('.')[-1].lower()
            array_word.append(tp)

        is_docx = False
        is_doc = False

        if 'docx' in array_word:
            is_docx = True

        if 'doc' in array_word:
            is_doc = True

        if not (is_docx or is_doc):
            return JsonResponse({"result": False, "message": _("Iltimos word fayl yuklang!")})

        if len(files) > 1:
            return JsonResponse({"result": False, "message": _("Iltimos faqat 1 ta word fayl yuklang!")})

        for f in files:
            tp = str(f).lower().split('.')[-1]

            if tp == 'doc' or tp == 'docx':
                number = question.test.number
                url = f"{main_folder}{number}"  # Path relative to media root
                full_url = os.path.join(media_root, url)

                if os.path.exists(question.test.file_word.path):
                    try:
                        path = question.test.file_word.path
                        os.remove(path)
                    except OSError as error:
                        print(error)
                        print("File path can not be removed")

                if not os.path.exists(full_url):
                    os.makedirs(full_url)

                fs = FileSystemStorage(location=full_url)
                filename = f"{number}.{tp}"

                saved_filename = fs.save(filename, f)
                file_url = os.path.join(url, saved_filename)

                test = get_object_or_404(Test, pk=question.test.id)
                test.file_word = file_url
                test.save()
                question.submission.topic_n = topic_n
                question.submission.save()
                question.status = get_object_or_404(StatusCheck, code=3)
                question.save()
            else:
                return JsonResponse({"result": False, "message": _(f".docx yoki .doc fayl yuklang!")})

            if question.submission.type_test_upload.id == 1:
                status_test = get_object_or_404(CheckTestExpertStatus, code=4)
                step = get_object_or_404(StepTest, code=0)
                try:
                    CheckTestExpert.objects.create(
                        user=user,
                        submission_test=question,
                        status_test=status_test,
                        step=step,
                        is_extra_expert=True,
                        job_number=3
                    )
                except Exception as e:
                    return JsonResponse({"result": False, "message": _(f"{e}")})

            if question.submission.type_test_upload.id == 2:
                status_test = get_object_or_404(CheckTestExpertStatus, code=4)
                step = get_object_or_404(StepTest, code=0)
                try:
                    CheckTestExpert.objects.create(
                        user=user,
                        submission_test=question,
                        status_test=status_test,
                        step=step,
                        is_extra_expert=True,
                        job_number=4
                    )
                except Exception as e:
                    return JsonResponse({"result": False, "message": _(f"{e}")})
            else:
                pass

            lang = get_language()
            url = f"/{lang}/test_maker/my_submit_tests/"
            if lang == 'uz':
                url = f"/test_maker/my_submit_tests/"
            return JsonResponse(
                {"result": True, "url": url, "message": _("Muvaffaqiyatli yuborildi!")})
        else:
            return JsonResponse({"result": False, "message": _("Forma to'liq emas!")})

    jobs = CheckTestExpert.objects.filter(submission_test=question, submission_test__is_editable=True).filter(
        Q(result=0) | Q(result=2) | Q(status__code=0) | Q(status__code=2)
    )

    criteria = []
    for job in jobs:
        items = JobControlSheetNS.objects.filter(job=job, result=0).order_by('control_sheet__code')
        criteria.append([items, job.job_number, job.status.code, job.message])

    context = {
        'submission': question,
        "form": EditSubmissionForm(instance=question.submission),
        "data": criteria,
    }
    return render(request, "test_maker/edit_test.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['expert', 'out_expert', 'admin', 'admin1'])
def my_submit_tests(request):
    user = request.user
    moderator = None
    labels1 = []
    data1 = []
    labels2 = []
    data2 = []
    data3 = []
    data4 = []
    total_questions = 0
    total_english_questions = 0
    expert = None
    if User.objects.filter(id=user.id).exists():
        user = get_object_or_404(User, pk=user.id)
    if Moderator.objects.filter(user=user).exists():
        moderator = get_object_or_404(Moderator, user=user)
    if user.is_admin1:
        tests = SubmissionTest.objects.filter(submission__type_test_upload_id=1).order_by('id')
        experts = Expert.objects.filter(is_expert=True, is_lang_specialist=True).order_by('id')
        moderators = Moderator.objects.filter(upload_type_id=1, is_moderator=True).order_by('id')

        total_questions = tests.count()
        total_english_questions = tests.filter(submission__subject__key='english').count()

        status_objects = StatusCheck.objects.all().order_by('code')
        for status in status_objects:
            labels1.append(status.name)
            data1.append(tests.filter(status__code=status.code).count())

        subjects = Subject.objects.filter(is_lang=True, status=True).order_by('id')
        for item in subjects:
            labels2.append(item.name)
            data2.append(tests.filter(submission__subject__key=item.key).count())
            data3.append(experts.filter(subject=item).count())
            data4.append(moderators.filter(subject=item).count())
    if user.is_expert:
        expert = get_object_or_404(Expert, user=user, is_expert=True)
    context = {
        "user": user,
        "expert": expert,
        "moderator": moderator,
        "labels1": labels1,
        "data1": data1,
        "labels2": labels2,
        "data2": data2,
        "data3": data3,
        "data4": data4,
        "total_questions": total_questions,
        "total_english_questions": total_english_questions,
    }
    return render(request, 'test_maker/my_submitted_tests.html', context)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def resend(request):
    return HttpResponse("Ok")


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def load_my_submit_tests_in_progress(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse({"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})

    page = None
    if 'page' in request.COOKIES:
        cookie_value = request.COOKIES['page']
        page = int(cookie_value)
    else:
        page = 1
    tests = SubmissionTest.objects.filter(user=user).order_by('-id')
    paginator = Paginator(tests, 10)
    page_obj = paginator.get_page(page)

    data = [test.get_data() for test in page_obj]

    num_pages = paginator.num_pages
    has_previous = page_obj.has_previous()

    previous_page_number = None
    if has_previous:
        previous_page_number = page_obj.previous_page_number()

    has_next = page_obj.has_next()

    next_page_number = None
    if has_next:
        next_page_number = page_obj.next_page_number()

    number = page_obj.number

    count_confirmed = 0
    items = TestConfirmationCount.objects.filter(user=user)
    for item in items:
        count_confirmed += item.count

    objects = CheckTestExpert.objects.filter(is_job_given=0, is_check=False).exclude(user=user)
    m_objects = None
    count_mwork = 0
    if user.is_moderator:
        m_objects = ModeratorCheckTest.objects.filter(is_job_given=0, is_check=False).exclude(user=user)
        count_mwork = m_objects.count()
    if user.is_expert:
        expert = get_object_or_404(Expert, user=user)
        objects = objects.filter(submission_test__submission__subject=expert.subject,
                                 submission_test__submission__lang=expert.lang_test)

        if expert.is_third_expert:
            objects = objects.filter(is_third_expert=True)
        elif not expert.is_third_expert:
            objects = objects.filter(is_third_expert=False)

        if expert.level is not None:
            objects = objects.filter(submission_test__submission__level_dn__ielts__lte=expert.level.ielts)

    count_work = objects.count()

    response = {
        "result": True,
        "num_pages": num_pages,
        "page": page,
        "has_previous": has_previous,
        "previous_page_number": previous_page_number,
        "has_next": has_next,
        "next_page_number": next_page_number,
        "number": number,
        "data": data,
        "count_confirmed": count_confirmed,
        "count_work": count_work,
        "count_mwork": count_mwork,
    }
    return JsonResponse(response, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def load_my_submit_tests_denied(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})

    tests = SubmissionTest.objects.filter(user=user).filter(status__code=0).order_by('id')
    data = [test.get_data() for test in tests]

    response = {
        "result": True,
        "data": data,
    }
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def subject_box(request):
    user = get_object_or_404(User, pk=request.user.id)
    teacher = get_object_or_404(Teacher, user=user)
    objects = SubjectBox.objects.filter(teacher=teacher)
    context = {
        "objects": objects
    }
    return render(request, "test_maker/tests.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def question_box(request, pk):
    subject_ob = get_object_or_404(SubjectBox, pk=pk)
    objects = QuestionBox.objects.filter(subject_box=subject_ob)
    context = {
        "objects": objects,
        "subject": subject_ob.subject,
    }
    return render(request, "test_maker/test_boxes.html", context=context)


@login_required(login_url='login')
def load_test_count(request):
    user = get_object_or_404(User, pk=request.user.id)
    if user.jshshr is None:
        return JsonResponse(
            {"result": False, "message": _("Shaxsiy ma'lumotlarizni kiriting!")})

    tests = SubmissionTest.objects.filter(user=user).filter(status__code=0).order_by('id')
    data = [test.get_data() for test in tests]

    response = {
        "result": True,
        "data": data,
    }
    return JsonResponse(response)


@allowed_users(role=['out_expert', 'expert', 'moderator'])
def set_cookie_view(request):
    if request.method == "GET" and is_ajax(request):
        page = request.GET.get('page')
        base_url = str(request._current_scheme_host).split(":")[1].replace('//', '')
        response = HttpResponse()
        response.set_cookie('page', f"{page}", domain=f"{base_url}", path="/")
        return response
    else:
        return HttpResponse("SetCookieda xatolik")


@allowed_users(role=['out_expert', 'expert', 'moderator'])
def delete_cookie_view(request):
    if request.method == "GET" and is_ajax(request):
        response = HttpResponse()
        response.delete_cookie('page')
        return response
    else:
        return HttpResponse("DeleteCookieda xatolik")


@login_required(login_url='login')
@allowed_users(role=['admin'])
def incoming_questions_dashboard(request):
    return render(request, 'test_maker/incoming_questions_dashboard.html')


@login_required(login_url='login')
@allowed_users(role=['admin'])
def load_incoming_questions(request):
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

        objects = SubmissionTest.objects.all().order_by('-id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(submission__subject__name__icontains=str(search_value).lower()) |
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(submission__topic__name__icontains=str(search_value).lower()) |
                Q(submission__part__name__icontains=str(search_value).lower()) |
                Q(submission__level_d__name__icontains=str(search_value).lower()) |
                Q(submission__type_test_upload__name__icontains=str(search_value).lower()) |
                Q(submission__level_dn__name__icontains=str(search_value).lower()),
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = '-id'

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
@allowed_users(role=['admin'])
def view_question(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin'])
def question_info(request, pk):
    question = get_object_or_404(SubmissionTest, pk=pk)
    objects = CheckTestExpert.objects.filter(submission_test=question).order_by('created_at')
    moderators = ModeratorCheckTest.objects.filter(submission_test=question)
    moderator = None
    if moderators.count() > 0:
        moderator = moderators.last()
    context = {
        "question": question,
        "objects": objects,
        "moderator": moderator,
    }
    return render(request, 'test_maker/question_info.html', context)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def get_work(request):
    user = get_object_or_404(User, pk=request.user.id)
    expert = get_object_or_404(Expert, user=user)
    subject = expert.subject
    lang = expert.lang_test

    m = CheckTestExpert.objects.filter(expert=expert, is_job_given=1,
                                       is_check=False).count()  # tugallanmagan ish bor yo'qligi
    if m > 0:
        data = {
            "result": 0,
            "message": "Ayni vaqta sizda tekshirilmagan ish mavjud!",
        }
        return JsonResponse(data=data)
    levels = LevelDifficultyNational.objects.all().order_by('id')
    ielts = [i.ielts for i in levels]

    objects = CheckTestExpert.objects.filter(is_job_given=0, is_check=False,
                                             submission_test__submission__subject=subject,
                                             submission_test__submission__lang=lang).exclude(user=user).order_by('id')
    if expert.level is not None:
        if expert.level.ielts in ielts:
            objects = objects.filter(submission_test__submission__level_dn__ielts__lte=expert.level.ielts)

    if expert.is_third_expert:
        objects = objects.filter(is_third_expert=True)
    elif not expert.is_third_expert:
        objects = objects.filter(is_third_expert=False)
    if objects.count() == 0:
        data = {
            "result": 0,
            "message": f"Ayni vaqta tizimda ish topilmadi!!",
        }
        return JsonResponse(data=data)

    job_ids = [item.id for item in objects]

    while True:
        if len(job_ids) == 0:
            data = {
                "result": 0,
                "message": f"Ayni vaqta tizimda ish topilmadi!!!",
            }
            return JsonResponse(data=data)
        select_random_id = np.random.choice(job_ids, 1, replace=False).tolist()
        work = get_object_or_404(CheckTestExpert, pk=int(select_random_id[0]))
        st = work.submission_test
        n_count = CheckTestExpert.objects.filter(submission_test=st, expert=expert, is_job_given=1, is_check=True).count()
        if n_count == 0:
            break
        elif n_count > 0:
            job_ids.remove(work.id)
            continue
        else:
            break

    work.expert = expert
    work.is_job_given = 1
    work.status_test = get_object_or_404(CheckTestExpertStatus, code=3)
    work.job_given_time = timezone.now()
    work.save()
    # 2-step
    work.submission_test.step = get_object_or_404(State, key=2)
    work.submission_test.save()

    if st.submission.type_test_upload.id == 1:
        part = st.submission.part
        level = st.submission.level_dn
        part_option_id = st.submission.part_option.id
        controls = ControlSheetNS.objects.filter(sheet__part=part, sheet__level=level, subject=work.submission_test.submission.subject, part_option_id=part_option_id).filter(status=True).order_by('id')

        for item in controls:
            try:
                JobControlSheetNS.objects.create(
                    job=work,
                    control_sheet=item,
                )
            except Exception as e:
                print(f"{e}")
                continue
    elif st.submission.type_test_upload.id == 2:
        controls = ControlSheet.objects.filter(sheet__id__in=[1,2,3]).order_by('id')
        for item in controls:
            JobControlSheet.objects.create(
                job=work,
                control_sheet=item,
            )

    data = {
        "result": 1,
        "message": f"Ok",
    }
    return JsonResponse(data=data)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_level_dn_list(request):
    levels = LevelDifficultyNational.objects.filter(status=True)
    data = [{'id': item.id, 'name': item.name} for item in levels]
    return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_part_option(request):
    type_upload_id = int(request.GET.get('type_upload_id'))
    subject_id = int(request.GET.get('subject_id'))
    lang_id = int(request.GET.get('lang_id'))
    level_id = int(request.GET.get('level_id'))
    part_id = request.GET.get('part_id')
    if part_id == '':
        data = []
        return JsonResponse(data, safe=False)
    elif str(part_id).isdigit():
        part_id = int(part_id)
        part_options = OptionPart.objects.filter(type_test_upload_id=type_upload_id, subject_id=subject_id,
                                                 lang_s_id=lang_id, part_id=part_id, level_id=level_id, status=True)
        data = [{'id': item.id, 'name': item.name} for item in part_options]
        return JsonResponse(data, safe=False)
    else:
        data = []
        return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert', 'moderator'])
def get_template_part_option(request):
    type_upload_id = int(request.GET.get('type_upload_id'))
    subject_id = int(request.GET.get('subject_id'))
    lang_id = int(request.GET.get('lang_id'))
    level_id = int(request.GET.get('level_id'))
    part_id = request.GET.get('part_id')
    part_option_id = request.GET.get('part_option_id')

    if part_id == '':
        data = []
        return JsonResponse(data, safe=False)
    elif str(part_id).isdigit():
        part_id = int(part_id)
        part_option_id = int(part_option_id)
        template = TemplateQuestion.objects.filter(type_test_upload_id=type_upload_id, subject_id=subject_id, lang_s_id=lang_id, part_id=part_id, level_id=level_id, part_option_id=part_option_id, status=True)
        template = template.last()
        data = {'id': template.id, 'name': template.part.name, 'file_url': template.template_file.url}
        return JsonResponse(data, safe=False)
    else:
        data = []
        return JsonResponse(data, safe=False)


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def get_rejected_jobcontrol(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['out_expert', 'expert'])
def get_rejected_jobcontrol_sheets(request, pk):
    try:
        question = get_object_or_404(SubmissionTest, pk=pk)
        if question.status.code == 0:
            status_reject = get_object_or_404(Status, code=0)
            job_objects = CheckTestExpert.objects.filter(submission_test=question, status=status_reject).order_by('job_number')
            criteria = []
            for job in job_objects:
                items1 = JobControlSheetNS.objects.filter(job=job, result=0).order_by('control_sheet__code')
                criteria.append([items1, job.job_number, job.status.code, job.message])

            m_job_objects = ModeratorCheckTest.objects.filter(submission_test=question, is_check=True, status__key=0)
            items2 = None
            if m_job_objects.count() == 1:
                job_m = get_object_or_404(ModeratorCheckTest, submission_test=question, is_check=True, status__key=0)
                items2 = ExpertiseQuestionJob.objects.filter(job=job_m, result=0).order_by('control_sheet__code')
            context = {"data": criteria, "data1": items2}
            return render(request, 'test_maker/view_criteria_info.html', context)
        else:
            criteria = []
            context = {"data": criteria, "data1": None}
            return render(request, 'test_maker/view_criteria_info.html', context)
    except Exception as e:
        return HttpResponse(f'Xatolik yuz berdi: {e}')

