from django.urls import path
from admin1.views import *

urlpatterns = [
    path('admin1_dashboard/', question_dashboard, name='admin1_dashboard'),
    path('load_questions_admin1/', load_questions_admin1, name='load_questions_admin1'),

    path('question_info/', view_question, name='view_question_admin1'),
    path('question_info/<int:pk>/', question_info, name='question_info_admin1'),

    path('expert_list_admin1/', expert_list_admin1, name='expert_list_admin1'),
    path('load_experts_admin1/', load_experts_admin1, name='load_experts_admin1'),

    path('expert_info/', view_expert, name='view_expert'),
    path('expert_info/<int:pk>/', expert_info, name='expert_info'),
    path('text_to_speech/', text_to_speech, name='text_to_speech'),
    path('load_converted_audios/', load_converted_audios, name='load_converted_audios'),
    path('delete_audio_object/<int:pk>/', delete_audio_object, name='delete_audio_object'),
    path('delete_audio_object/', delete_audio, name='delete_audio'),
    path('generate_text/', generate_text, name='generate_text'),
    path('load_converted_texts/', load_converted_texts, name='load_converted_texts'),
    path('delete_text/<int:pk>/', delete_text_object, name='delete_text_object'),
    path('delete_text/', delete_text, name='delete_text'),
    path('generate_test/', g_test, name='g_test'),
    path('generate_test/<int:pk>/', generate_test, name='generate_test'),
    path('delete_test/<int:pk>/', delete_test, name='delete_test'),

    path('blocking_expert/', blocking_expert, name='blocking_expert'),
    path('blocking_expert/<int:pk>/', blocked_expert, name='blocked_expert'),
    path('un_blocking_expert/', un_blocking_expert, name='un_blocking_expert'),
    path('un_blocking_expert/<int:pk>/', un_blocked_expert, name='un_blocked_expert'),

    path('edit_expert_permission/', edit_expert_permission_url, name='edit_expert_permission_url'),
    path('edit_expert_permission/<int:pk>/', edit_expert_permission, name='edit_expert_permission'),

    path('load_question_count_menu/', load_question_count_menu, name='load_question_count_menu'),
    path('load_sending_question_count_list/', load_sending_question_count_list, name='load_sending_question_count_list'),

    path('load_question_payment_menu/', load_question_payment_menu, name='load_question_payment_menu'),
    path('load_question_payment_list/', load_question_payment_list, name='load_question_payment_list'),
]