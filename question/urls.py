from django.urls import path
from question.views import *

urlpatterns = [
    path('admission_dashboard/', admission_dashboard, name='admission_dashboard'),
    path('get_admission_questions/', get_admission_questions, name='get_admission_questions'),
    path('national_dashboard/', national_dashboard, name='national_dashboard'),
    path('load_question_national/', load_question_national, name='load_question_national'),
    path('view_question_national/', view_question, name='view_question'),
    path('view_question_admission/', view_question, name='view_question_a'),
    path('view_question_national/<int:pk>/', view_question_national, name='view_question_national'),
    path('view_question_admission/<int:pk>/', view_question_admission, name='view_question_admission'),
]
