from django.urls import path
from expert.views import *

urlpatterns = [
    # Export dashboard
    path('expert_dashboard/', expert_dashboard, name='expert_dashboard'),
    path('expert_list/', expert_list, name='expert_list'),
    path('expert_list/<int:pk>/', edit_third_expert, name='edit_third_expert'),
    path('get_experts/', get_experts, name='get_experts'),
    path('check_have_certificate/<int:pk>/', check_have_certificate, name='check_have_certificate'),
    path('load_test_for_expert/', load_test_for_expert, name='load_test_for_expert'),
    path('load_test_for_expert/<int:pk>/', check_current_test_expert, name='check_current_test_expert'),
    path('is_have_unchecked_job/', is_have_unchecked_job, name='is_have_unchecked_job'),
    path('load_checked_jobs/', load_checked_jobs, name='load_checked_jobs'),
    path('upload_certificate/', upload_certificate, name='upload_certificate'),
]