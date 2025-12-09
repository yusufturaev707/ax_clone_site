from django.urls import path

from fileapp.views import *

urlpatterns = [
    path('files_list/', files_list, name='files_list'),
]