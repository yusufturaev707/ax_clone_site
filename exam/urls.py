from django.urls import path
from exam.views import *

urlpatterns = [
    path('test_detail/<int:qbox_id>/', test_detail, name='test_detail'),
    path('create_exam/<int:qbox_id>/', create_exam, name='create_exam'),
    path('exam_room/<int:pk>/', exam_room, name='exam_room'),
    path('load_questions/', load_questions, name='load_questions'),
    path('load_questions/<int:pk>/', get_question, name='get_question'),
    path('timer_view/<int:pk>/', timer_view, name='timer_view'),
    path('next_question/', next_question, name='next_question'),
    path('set_cookie_view/', set_cookie_view, name='set_cookie_view'),
    path('delete_cookie_view/', delete_cookie_view, name='delete_cookie_view'),
    path('exam_finished/<int:pk>/', exam_finished, name='exam_finished'),
    path('exam_finish_btn/<int:pk>/', exam_finish_btn, name='exam_finish_btn'),
    path('exam_result/<int:pk>/', exam_result, name='exam_result'),
    path('exam_result_dash/<int:pk>/', exam_result_dash, name='exam_result_dash'),
    path('appeal/', appeals, name='appeals'),
    path('appeal/<int:pk>/', appeal, name='appeal'),
]
