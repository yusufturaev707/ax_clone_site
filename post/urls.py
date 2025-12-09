from django.urls import path

from post.views import *

urlpatterns = [
    path('post_dashboard/', post_dashboard, name='post_dashboard'),
    path('page_dashboard/', page_dashboard, name='page_dashboard'),
    path('create_post/', create_post, name='create_post'),
    path('create_page/', create_page, name='create_page'),
    path('<slug:slug>/', post_detail, name='post_detail'),
    path('edit_post/<int:pk>/', edit_post, name='edit_post'),
    path('delete_post/<int:pk>/', delete_post, name='delete_post'),
    path('edit_page/<int:pk>/', edit_page, name='edit_page'),
    path('delete_page/<int:pk>/', delete_page, name='delete_page'),
]