from django.urls import path

from journal.views import *

urlpatterns = [
    path('dashboard/', journal_dashboard, name='journal_dashboard'),
    path('archive_journals/', archive_journals, name='archive_journals'),
    path('archive_journals_numbers/<int:year>/', archive_journals_numbers, name='archive_journals_numbers'),
    path('archive_journals_articles/<int:pk>/', archive_journals_articles, name='archive_journals_articles'),
    path('archive_article_review/<int:pk>/', archive_article_review, name='archive_article_review'),
    path('select_article_orders/', select_article_orders, name='select_article_orders'),
    path('create/', create_journal, name='create_journal'),
    path('view/<int:pk>/', journal_detail, name='view_journal'),
    path('edit/<int:pk>/', edit_journal, name='edit_journal'),
    path('delete/<int:pk>/', delete_journal, name='delete_journal'),
    # path('split_pages/<int:pk>/', split_journal_pages, name='split_journal_pages'),
    path('journals_list/', journals_list, name='journals_list'),
    path('upload_template/', upload_template, name='upload_template'),
    path('article_view/<int:pk>/', journal_article_view, name='journal_article_view'),
    path('journal_year_list/<int:year>/', journal_year_list, name='journal_year_list'),
    path('upload_checked_file/<int:pk>/', upload_checked_file, name='upload_checked_file'),
    path('update_checked_article/<int:pk>/', update_checked_article, name='update_checked_article'),
    path('journal_years_list/', journal_years_list, name='journal_years_list'),
    path('journal_years_list/create/', create_journal_year, name='create_journal_year'),
    path('journal_years_list/edit/<int:pk>/', edit_journal_year, name='edit_journal_year'),
    path('journal_years_list/delete/<int:pk>/', delete_journal_year, name='delete_journal_year'),
    path('journal_numbers_list/', journal_numbers_list, name='journal_numbers_list'),
    path('journal_numbers_list/create/', create_journal_number, name='create_journal_number'),
    path('journal_numbers_list/edit/<int:pk>/', edit_journal_number, name='edit_journal_number'),
    path('journal_numbers_list/delete/<int:pk>/', delete_journal_number, name='delete_journal_number'),
]
