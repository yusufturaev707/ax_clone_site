from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

from question.models import QuestionAdmission, QuestionNational
from user_app.decorators import allowed_users
from django.db.models import Q


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['admin'])
def admission_dashboard(request):
    return render(request, 'question/admission_table.html')


@login_required(login_url='login')
@allowed_users(role=['admin'])
def get_admission_questions(request):
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

        objects = QuestionAdmission.objects.all().order_by('id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(number__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(subject__name__icontains=str(search_value).lower()) |
                Q(language__name__icontains=str(search_value).lower()) |
                Q(theme__name__icontains=str(search_value).lower()) |
                Q(level__name__icontains=str(search_value).lower()) |
                Q(status__name__icontains=str(search_value).lower())
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = 'id'

        questions = objects.order_by(sort_column_name)
        questions = questions[start:limit]

        response = {
            "data": list(questions.values(
                'id', 'number', 'submission_test_id', 'user__last_name',
                'user__first_name', 'user__middle_name', 'subject__name', 'language__name',
                'theme__name', 'level__name', 'tex_code', 'a', 'b', 'c', 'd', 'tex_file',
                'question_pdf', 'option_pdf', 'status__name', 'created_at', 'updated_at'
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
def national_dashboard(request):
    return render(request, 'question/national_table.html')


@login_required(login_url='login')
@allowed_users(role=['admin'])
def load_question_national(request):
    questions = QuestionNational.objects.all().order_by('id')
    data = [question.get_data() for question in questions]
    response = {"data": data}
    return JsonResponse(response)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def view_question(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin'])
def view_question_national(request, pk):
    question = get_object_or_404(QuestionNational, pk=pk)
    context = {
        "question": question
    }
    return render(request, 'question/view_question.html', context)


@login_required(login_url='login')
@allowed_users(role=['admin'])
def view_question_admission(request, pk):
    question = get_object_or_404(QuestionAdmission, pk=pk)
    context = {
        "question": question
    }
    return render(request, 'question/view_question_qabul.html', context)
