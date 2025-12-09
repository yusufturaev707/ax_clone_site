from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('contact/', contact, name='contact'),
    path('technical_support/', technical_support, name='technical_support'),
    path('about_journal/', about_journal, name='about_journal'),
    path('editor_board/', editor_board, name='editor_board'),
    path('guide_for_authors/', guide_for_authors, name='guide_for_authors'),
    path('load_sidebar_menus/', load_sidebar_menus, name='load_sidebar_menus'),
    path('load_navbar_menus/', load_navbar_menus, name='load_navbar_menus'),

    path('article/create/', create_article, name='create_article'),
    path('article/view/<int:pk>/', article_view, name='article_view'),
    path('article/edit/<int:pk>/', update_article, name='update_article'),
    path('article/delete/<int:pk>/', delete_article, name='delete_article'),
    path('article/file/create/<int:pk>/', create_article_file, name='create_article_file'),

    path('authors/<int:pk>/', get_article_authors, name='get_article_authors'),
    path('author/add/<int:pk>/', add_author, name='add_author'),
    path('author/edit/<int:pk>/', edit_author, name='edit_author'),
    path('author/delete/<int:pk>/', delete_author, name='delete_author'),

    path('send_message/<int:pk>/<int:user_id>/', send_message, name='send_message'),

    path('sections/', list_sections, name='sections'),
    path('sections/create/', create_section, name='create_section'),
    path('sections/edit/<int:pk>/', edit_section, name='edit_section'),
    path('sections/delete/<int:pk>/', delete_section, name='delete_section'),

    path('article_types/', article_type_list, name='article_types'),
    path('article_types/create/', create_article_type, name='create_article_type'),
    path('article_types/edit/<int:pk>/', edit_article_type, name='edit_article_type'),
    path('article_types/delete/<int:pk>/', delete_article_type, name='delete_article_type'),

    path('article_stages/', article_stages_list, name='article_stages'),
    path('article_stages/create/', create_stage, name='create_stage'),
    path('article_stages/edit/<int:pk>/', edit_stage, name='edit_stage'),
    path('article_stages/delete/<int:pk>/', delete_stage, name='delete_stage'),

    path('article_status/', article_status_list, name='article_status'),
    path('article_status/create/', create_article_status, name='create_article_status'),
    path('article_status/edit/<int:pk>/', edit_article_status, name='edit_article_status'),
    path('article_status/delete/<int:pk>/', delete_article_status, name='delete_article_status'),

    path('notification_status/', notification_status_list, name='notification_status'),
    path('notification_status/create/', create_notification_status, name='create_notification_status'),
    path('notification_status/edit/<int:pk>/', edit_notification_status, name='edit_notification_status'),
    path('notification_status/delete/<int:pk>/', delete_notification_status, name='delete_notification_status'),

    path('last_journal/', last_journal, name='last_journal'),

]
