from django.urls import path
from moderator.views import *

urlpatterns = [
    path('moderator_dashboard/', moderator_dashboard, name='moderator_dashboard'),
    path('moderator_list/', moderator_list, name='moderator_list'),
    path('get_moderators/', get_moderators, name='get_moderators'),
    path('load_test_moderator/', load_test_moderator, name='load_test_moderator'),
    path('load_test_moderator/<int:pk>/', convert_to_tex, name='convert_to_tex'),
    path('pass_saving/<int:pk>/', pass_saving, name='pass_saving'),
    path('view_image_path/<int:pk>/', view_image_path, name='view_image_path'),
    path('delete_image/<int:pk>/', delete_image, name='delete_image'),
    path('get_work_for_moderator/', get_work_for_moderator, name='get_work_for_moderator'),

    path('check_status/', check_status, name='check_status'),
    path('check_status/<int:pk>/', check_status_id, name='check_status_id'),
    path('checking_job/', checking_job, name='checking_job'),
    path('checking_job/<int:pk>/', checking_job_window, name='checking_job_window'),
]
