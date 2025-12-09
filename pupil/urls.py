from django.urls import path
from pupil.views import *

urlpatterns = [
    path('pupil_dashboard/', pupil_dashboard, name='pupil_dashboard'),
    path('personal_data/', personal_data, name='personal_data'),
    path('get_districts/', get_districts, name='get_districts'),
    path('subjects/', subjects, name='subjects'),
    path('request_token/<int:pk>/', request_token, name='request_token'),
]
