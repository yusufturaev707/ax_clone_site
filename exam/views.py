import datetime
import os
from subprocess import check_output
import platform
import random
import time

from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _, get_language

from config import settings
from exam.forms import AppealForm
from exam.models import Exam, ExamQuestion, PupilResponse, Appeal, Category
from pupil.models import Pupil
from test_maker.models import QuestionBox
from user_app.decorators import allowed_users
from user_app.models import User


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['pupil'])
def test_detail(request, qbox_id):
    qbox = get_object_or_404(QuestionBox, pk=qbox_id)
    subject = qbox.subject_box.subject
    duration = qbox.subject_box.subject.duration
    box_number = qbox.box_number
    count_question = qbox.count_question
    qbox_id = qbox.id

    context = {
        "subject": subject,
        "duration": duration,
        "qbox": qbox,
        "box_number": box_number,
        "count_question": count_question,
        "qbox_id": qbox_id,
    }
    return render(request, "exam/alert_test.html", context)


media_url = settings.MEDIA_URL
media_root = settings.MEDIA_ROOT
main_folder = "exams/"


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def create_exam(request, qbox_id):
    if request.method == 'POST' and is_ajax(request):
        user = get_object_or_404(User, pk=request.user.id)
        pupil = get_object_or_404(Pupil, user=user)
        qbox = get_object_or_404(QuestionBox, pk=qbox_id)
        subject = qbox.subject_box.subject
        exam = None

        exams = Exam.objects.filter(question_box__subject_box__subject=subject, question_box=qbox)
        if exams.count() == 0:
            exam = Exam.objects.create(
                pupil=pupil,
                subject=subject,
                question_box=qbox,
                duration=subject.duration,
                is_started=True,
            )
            order = 1
            questons = qbox.questions.all()
            n = questons.count()
            for question in questons:
                q = [question.a, question.b, question.c, question.d]

                a = []
                while len(a) != 4:
                    t = random.randint(0, 3)
                    if t in a:
                        continue
                    a.append(t)

                b = []
                for i in a:
                    b.append(q[i])
                correct_index = a.index(0)

                text = question.tex_code.replace('\end{document}', '')
                text = text + "\n\n" + f"A){b[0]}" + "\n\n" + f"B){b[1]}" + "\n\n" + f"C){b[2]}" + "\n\n" + f"D){b[3]}" + "\n" + "\end{document}"

                url = f"{main_folder}{pupil.id}/{exam.id}/"
                name = f"{pupil.id}{qbox.id}{exam.id}{question.id}"
                full_url = f"{media_root}{url}"

                if not os.path.exists(full_url):
                    os.makedirs(full_url)

                with open(f"{full_url}{name}.tex", 'w', encoding="utf-8") as file:
                    file.write(text)

                from subprocess import check_output

                command = f"pdflatex -output-directory {full_url}"
                tex_file = f"{full_url}{name}.tex"

                plt = platform.system()

                if plt == "Windows":
                    check_output(f"{command} {tex_file}", shell=True)
                elif plt == "Linux":
                    os.system(command=f"{command} {tex_file}")

                file_aux = f"{full_url}{name}.aux"

                if os.path.exists(file_aux):
                    os.remove(file_aux)
                    print(f"File '{file_aux}' has been removed.")

                if n == order:
                    ExamQuestion.objects.create(
                        exam=exam,
                        question=question,
                        correct_answer=correct_index,
                        pdf=f"{url}{name}.pdf",
                        order_q=order,
                        is_last_question=True
                    )
                if order < n:
                    ExamQuestion.objects.create(
                        exam=exam,
                        question=question,
                        correct_answer=correct_index,
                        pdf=f"{url}{name}.pdf",
                        order_q=order,
                    )
                order += 1
        else:
            data = {
                'message': f"Siz {qbox.box_number}-variantni oldin ishlagansiz.",
                'exam_id': 0
            }
            return JsonResponse(data)
        data = {
            'message': "Success",
            'exam_id': exam.id
        }
        return JsonResponse(data)
    else:
        return HttpResponse("Error")


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def exam_room(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    fio = exam.pupil.user.full_name
    return render(request, "exam/exam_room.html", {
        "examID": exam.id,
        "fio": fio,
        "subject": exam.subject.name,
        "is_finished": exam.is_finished,
    })


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def exam_result(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    results = PupilResponse.objects.filter(exam=exam, exam__is_finished=True).order_by('question__order_q')
    start_time = exam.start_time
    finish_time = exam.finish_time
    score = exam.score
    count_correct = exam.count_correct_answer
    count_incorrect = exam.count_incorrect_answer
    fio = exam.pupil.user.full_name
    subject = exam.subject.name

    context = {
        "results": results,
        "start_time": start_time,
        "finish_time": finish_time,
        "score": score,
        "count_correct": count_correct,
        "count_incorrect": count_incorrect,
        "fio": fio,
        "subject": subject,
    }
    return render(request, "exam/result_info.html", context=context)


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def exam_result_dash(request, pk):
    user = get_object_or_404(User, pk=request.user.id)
    exam = get_object_or_404(Exam, pk=pk)
    if exam.pupil.user == user:
        results = PupilResponse.objects.filter(exam=exam, exam__is_finished=True).order_by('question__order_q')
        start_time = exam.start_time
        finish_time = exam.finish_time
        score = exam.score
        count_correct = exam.count_correct_answer
        count_incorrect = exam.count_incorrect_answer
        fio = exam.pupil.user.full_name
        subject = exam.subject.name

        context = {
            "results": results,
            "start_time": start_time,
            "finish_time": finish_time,
            "score": score,
            "count_correct": count_correct,
            "count_incorrect": count_incorrect,
            "fio": fio,
            "subject": subject,
        }
        return render(request, "exam/result.html", context=context)
    else:
        return HttpResponse("Sizga tegishlimas")


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def load_questions(request):
    if request.method == 'GET' and is_ajax(request):
        exam_id = request.GET.get('examID')

        exam = get_object_or_404(Exam, pk=int(exam_id))
        if exam.is_finished:
            data = {
                "message": "Vaqtingiz tugadi",
                "is_finished": exam.is_finished,
            }
            return JsonResponse(data)
        else:
            questions = ExamQuestion.objects.filter(exam=exam).order_by('id')

            if exam.finish_time is None:
                duration = str(exam.duration).split(':')
                h = duration[0]
                m = duration[1]
                s = duration[2]
                interval = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                exam.finish_time = exam.start_time + interval
                exam.save()
            q_id = None
            if 'question_id' in request.COOKIES:
                cookie_value = request.COOKIES['question_id']
                q_id = int(cookie_value)
            else:
                q_id = questions.first().id
                print("The cookie 'my_cookie_name' does not exist.")

            question = get_object_or_404(ExamQuestion, pk=q_id)

            data = {
                "questions": list(questions.values(
                    'id', 'order_q', 'is_solved'
                )),
                "is_solved": question.is_solved,
                "pdf_url": question.pdf.url,
                "question_id": question.id,
                "question_order": question.order_q,
                "is_finished": exam.is_finished,

            }
            return JsonResponse(data)
    else:
        return HttpResponse('Xatolik load_questions')


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def get_question(request, pk):
    if request.method == 'GET' and is_ajax(request):
        question = get_object_or_404(ExamQuestion, pk=pk)
        base_url = request._current_scheme_host
        res1 = None
        res2 = None
        v = ["#answerA", "#answerB", "#answerC", "#answerD"]
        r = ["#radioA", "#radioB", "#radioC", "#radioD"]
        if question.is_solved:
            p_response = get_object_or_404(PupilResponse, question=question)
            res1 = v[p_response.selected_answer]
            res2 = r[p_response.selected_answer]

        data = {
            "id": question.id,
            "pdf_url": f"{base_url}{question.pdf.url}",
            "is_solved": question.is_solved,
            "exam_id": question.exam.id,
            "question_order": question.order_q,
            "res1": res1,
            "res2": res2,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('Xatolik')


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def timer_view(request, pk):
    if request.method == 'GET' and is_ajax(request):
        exam = get_object_or_404(Exam, pk=pk)
        c_time = datetime.datetime.now()
        f_time = exam.finish_time

        data = {
            "message": "Success",
            "current_time": c_time,
            "finish_time": f_time,
            "is_finish": exam.is_finished,
        }
        return JsonResponse(data)
    else:
        return HttpResponse('Xatolik timer_view')


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def exam_finished(request, pk):
    if request.method == 'GET' and is_ajax(request):
        exam = get_object_or_404(Exam, pk=pk)
        c_time = datetime.datetime.now()
        f_time = exam.finish_time

        current_time = datetime.datetime.strftime(c_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        finish_time = datetime.datetime.strftime(f_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        if current_time >= finish_time:
            n = ExamQuestion.objects.filter(exam=exam).count()
            b = 100 / n
            exam.is_finished = True

            no_solved_q = ExamQuestion.objects.filter(exam=exam, is_solved=False)

            if no_solved_q.count() > 0:
                for question in no_solved_q:
                    PupilResponse.objects.create(
                        exam=exam,
                        question=question,
                    )

            correct_res = PupilResponse.objects.filter(exam=exam, is_correct_answer=True)
            exam.score = correct_res.count() * b
            exam.count_correct_answer = correct_res.count()
            exam.count_incorrect_answer = n - correct_res.count()
            exam.save()

            objects = ExamQuestion.objects.filter(exam=exam, exam__is_finished=True).order_by('order_q')
            for obj in objects:
                if os.path.exists(obj.pdf.path):
                    try:
                        path = obj.pdf.path
                        path_tex = f"{path}".replace('.pdf', '.tex')
                        path_log = f"{path}".replace('.pdf', '.log')
                        os.remove(path_tex)
                        os.remove(path_log)
                        os.remove(path)
                    except OSError as error:
                        print(error)
                        print("File path can not be removed")
        else:
            print(f"Vaqt tugamagan")
        data = {
            "message": "Success",
        }
        return JsonResponse(data)
    else:
        return HttpResponse('Xatolik finished')


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def exam_finish_btn(request, pk):
    if request.method == 'GET' and is_ajax(request):
        exam = get_object_or_404(Exam, pk=pk)
        count_q = ExamQuestion.objects.filter(exam=exam).count()
        b = 100 / count_q
        no_solved_q = ExamQuestion.objects.filter(exam=exam, is_solved=False)

        if no_solved_q.count() > 0:
            for question in no_solved_q:
                PupilResponse.objects.create(
                    exam=exam,
                    question=question,
                )

        exam.is_finished = True
        correct_res = PupilResponse.objects.filter(exam=exam, is_correct_answer=True)
        exam.score = correct_res.count() * b
        exam.count_correct_answer = correct_res.count()
        exam.count_incorrect_answer = count_q - correct_res.count()
        exam.save()

        objects = ExamQuestion.objects.filter(exam=exam, exam__is_finished=True).order_by('order_q')
        for obj in objects:
            if os.path.exists(obj.pdf.path):
                try:
                    path = obj.pdf.path
                    path_tex = f"{path}".replace('.pdf', '.tex')
                    path_log = f"{path}".replace('.pdf', '.log')
                    os.remove(path_tex)
                    os.remove(path_log)
                    os.remove(path)
                except OSError as error:
                    print(error)
                    print("File path can not be removed")
        data = {
            "message": "Success",
        }
        return JsonResponse(data)
    else:
        return HttpResponse('Xatolik finished')


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def next_question(request):
    if request.method == 'POST' and is_ajax(request):
        result = request.POST.get('test' or None)
        q_id = request.POST.get('question_id')

        if result is None:
            data = {
                "result": 0,
                "message": "Javob belgilanmadi!",
            }
            return JsonResponse(data)

        if str(q_id).isdigit() and int(q_id) > 0:
            items = ExamQuestion.objects.filter(pk=int(q_id))
            if items.count() == 0:
                data = {
                    "result": 0,
                    "message": "Ma'lumot yuklanmadi!",
                }
                return JsonResponse(data)

        current_q = get_object_or_404(ExamQuestion, pk=int(q_id))
        exam = current_q.exam

        is_correct_answer = False
        if current_q.correct_answer == int(result):
            is_correct_answer = True

        variant = ['A', 'B', 'C', 'D']

        if current_q.is_solved:
            question = PupilResponse.objects.get(exam=exam, question=current_q)
            question.is_correct_answer = is_correct_answer
            question.selected_answer = int(result)
            question.selected_abcd = variant[int(result)]
            question.save()
        else:
            current_q.is_solved = True
            PupilResponse.objects.create(
                exam=exam,
                question=current_q,
                selected_answer=int(result),
                selected_abcd=variant[int(result)],
                is_correct_answer=is_correct_answer
            )
            current_q.save()

        if current_q.is_last_question:
            data = {
                "result": 2,
                "last_id": current_q.id,
                "message": "Bu oxirgi savol edi!",
            }
            return JsonResponse(data)

        next_order_q = current_q.order_q + 1
        get_next_question = get_object_or_404(ExamQuestion, order_q=next_order_q)
        base_url = request._current_scheme_host

        res1 = None
        res2 = None
        v = ["#answerA", "#answerB", "#answerC", "#answerD"]
        r = ["#radioA", "#radioB", "#radioC", "#radioD"]
        if get_next_question.is_solved:
            p_response = get_object_or_404(PupilResponse, question=get_next_question)
            res1 = v[p_response.selected_answer]
            res2 = r[p_response.selected_answer]

        data = {
            "result": 1,
            "id": get_next_question.id,
            "last_id": current_q.id,
            "pdf_url": f"{base_url}{get_next_question.pdf.url}",
            "is_solved": get_next_question.is_solved,
            "exam_id": exam.id,
            "question_order": get_next_question.order_q,
            "is_last_question": current_q.is_last_question,
            "res1": res1,
            "res2": res2,
        }
        return JsonResponse(data)


@allowed_users(role=['pupil'])
def set_cookie_view(request):
    if request.method == "GET" and is_ajax(request):
        question_id = request.GET.get('question_id')
        base_url = str(request._current_scheme_host).split(":")[1].replace('//', '')
        response = HttpResponse()
        response.set_cookie('question_id', f"{question_id}", max_age=3600, domain=f"{base_url}", path="/")
        return response
    else:
        return HttpResponse("SetCookieda xatolik")


@allowed_users(role=['pupil'])
def delete_cookie_view(request):
    if request.method == "GET" and is_ajax(request):
        response = HttpResponse()
        response.delete_cookie('question_id')
        return response
    else:
        return HttpResponse("DeleteCookieda xatolik")


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def appeal(request, pk):
    form = AppealForm()
    pupil = get_object_or_404(Pupil, user=request.user)
    question = get_object_or_404(ExamQuestion, pk=pk)

    if request.method == "POST" and is_ajax(request):
        ct = request.POST.get('category', None)
        cn = request.POST.get('content', None)
        if ct == '' or cn == '':
            data = {
                "result": 1,
                "message": "Etiroz turi yoki Izoh kiritilmadi!",
            }
            return JsonResponse(data)

        form = AppealForm(request.POST)
        if form.is_valid():
            exam_id = request.POST.get('exam')
            question_id = request.POST.get('question')
            pupil_id = request.POST.get('pupil')

            is_exists_db = Appeal.objects.filter(pupil__id=int(pupil_id), exam__id=int(exam_id), question__id=int(question_id)).exists()
            if not is_exists_db:
                form.save()
                data = {
                    "result": 2,
                    "message": "Muvaffaqiyatli yuborildi",
                }
                return JsonResponse(data)
            else:
                ob = get_object_or_404(Appeal, pupil__id=int(pupil_id), exam__id=int(exam_id), question__id=int(question_id))
                ob.category = get_object_or_404(Category, pk=int(ct))
                ob.content = str(cn)
                ob.save()

                data = {
                    "result": 2,
                    "message": "Muvaffaqiyatli yuborildi",
                }
                return JsonResponse(data)

        else:
            data = {
                "result": 1,
                "message": "Forma valid emas!",
            }
            return JsonResponse(data)

    context = {
        "form": form,
        "question": question,
        "pupil": pupil,
    }
    return render(request, "exam/etiroz.html", context=context)


@allowed_users(role=['pupil'])
@login_required(login_url='login')
def appeals(request):
    return render(request, "exam/result_info.html")
