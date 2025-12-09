from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from exam.models import Exam
from pupil.models import Pupil
from question.models import QuestionAdmission
from test_maker.models import Subject, Teacher, QuestionBox
from user_app.decorators import allowed_users
from user_app.models import User, Region, District
from django.utils.translation import get_language


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(['pupil'])
def pupil_dashboard(request):
    user = User.objects.get(pk=request.user.id)
    objects = Exam.objects.filter(pupil__user_id=user.id)
    context = {
        "user": user,
        "objects": objects,
    }
    return render(request, "pupil/pupil_dashboard.html", context)


@login_required(login_url='login')
def personal_data(request):
    user = get_object_or_404(User, pk=request.user.id)
    pupil = get_object_or_404(Pupil, user=user)
    if request.method == "POST":
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        learning_center = request.POST.get('learning_center')
        address = request.POST.get('address')

        user.username = username
        user.phone = phone
        user.save()

        pupil.learning_center = learning_center
        pupil.address = address
        pupil.save()

        return JsonResponse(data={"message": "Muvaffaqiyatli saqlandi"})

    regions = Region.objects.all().order_by('name')
    context = {
        "pupil": pupil,
        "regions": regions,
    }
    return render(request, "pupil/personal_data.html", context=context)


@login_required(login_url='login')
def get_districts(request):
    region_id = request.GET.get('region_id')
    region = get_object_or_404(Region, pk=int(region_id))
    districts = District.objects.filter(region=region).order_by('name')
    data = {
        'districts': list(districts.values(
            'id', 'name'
        )),
    }
    return JsonResponse(data)


@login_required(login_url='login')
def subjects(request):
    objects = Subject.objects.filter(status=True).order_by('id')
    context = {
        "objects": objects,
    }
    return render(request, "pupil/subjects.html", context=context)


@login_required(login_url='login')
def request_token(request, pk):
    subject_ob = get_object_or_404(Subject, pk=pk)
    pupil = get_object_or_404(Pupil, user=request.user)
    if request.method == "POST" and is_ajax(request):
        token = request.POST.get('teacher_token', None)
        try:
            teacher = get_object_or_404(Teacher, token_for_pupil=token)
        except Exception as e:
            data = {
                "result": 0,
                "message": f"{e}"
            }
            return JsonResponse(data)
        question_boxes = QuestionBox.objects.filter(subject_box__teacher_id=teacher.id,
                                                    subject_box__subject_id=subject_ob.id, count_question__gte=5)

        if not pupil.is_full_personal_data:
            data = {
                "result": 3,
                "message": f"Shaxsiy ma'lumotlar to'liq emas!"
            }
            return JsonResponse(data)

        if question_boxes.count() == 0:
            data = {
                "result": 2,
                "message": f"Variantlar topilmadi"
            }
            return JsonResponse(data)

        data = {
            "result": 1,
            "question_boxes": list(question_boxes.values(
                'id', 'box_number', 'count_question', 'subject_box_id', 'subject_box__teacher_id',
                'subject_box__subject_id', 'subject_box__subject__name'
            ))
        }
        return JsonResponse(data)
    context = {
        "subject": subject_ob
    }
    return render(request, 'pupil/request_token.html', context)
