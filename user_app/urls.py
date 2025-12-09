from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from user_app.views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('user_dashboard/', user_dashboard, name='dashboard'),
    path('editor_dashboard/', editor_dashboard, name='editor_dashboard'),
    path('reviewer_dashboard/', reviewer_dashboard, name='reviewer_dashboard'),
    path('editor_notifications/', editor_notifications, name='editor_notifications'),
    path('reviewer_notifications/', reviewer_notifications, name='reviewer_notifications'),

    path('load_notif_count/', load_notif_count, name='load_notif_count'),
    path('get_data_ps/', get_data_ps, name='get_data_ps'),

    path('editor_check_article/<int:pk>/', editor_check_article, name='editor_check_article'),
    path('editor_submit_result/', editor_submit_result, name='editor_submit_result'),

    path('reviewer_check_article/<int:pk>/', reviewer_check_article, name='reviewer_check_article'),

    path('article_notification/view/<int:pk>/', author_vs_editor_vs_reviewer, name='comment_author_vs_editor'),

    path('load_notif/', load_notification, name='load_notification'),
    path('count_notif/', count_notification, name='count_notification'),
    path('load_reviewers/<int:article_id>/', load_reviewers, name='load_reviewers'),
    path('sending_reviewer/', sending_reviewer, name='sending_reviewer'),
    path('random_sending_reviewer/', random_sending_reviewer, name='random_sending_reviewer'),

    path('reviewer_confirmed/<int:pk>/', reviewer_confirmed, name='reviewer_confirmed'),
    path('reviewer_resubmit/', reviewer_resubmit, name='reviewer_resubmit'),
    path('reviewer_rejected/', reviewer_rejected, name='reviewer_rejected'),

    path('approve_publish/', approve_publish, name='approve_publish'),
    path('editor_resubmit_to_reviewer/', editor_resubmit_to_reviewer, name='editor_resubmit_to_reviewer'),

    path('login/', login_page, name='login'),
    path('logout', logout_user, name='logout'),
    path('register/', register_page, name='register'),
    path('choosen_reviewer_role/', choose_roles, name='choosen_reviewer_role'),
    path('choosen_reviewer_role_list/', reviewer_role_list, name='choosen_reviewer_role_list'),
    path('choosen_reviewer_role_list/<int:pk>/', reviewer_role_list_detail, name='reviewer_role_list_detail'),

    path('edit_profile/', edit_profile, name='edit_profile'),
    path('load_menus/', load_menus, name='load_menus'),
    path('reviewers_list/', reviewers_list, name='reviewers_list'),

    path('countries/', countries_list, name='countries'),
    path('countries/create/', create_country, name='create_country'),
    path('countries/edit/<int:pk>/', edit_country, name='edit_country'),
    path('countries/delete/<int:pk>/', delete_country, name='delete_country'),

    path('editors/', editors_list, name='editors'),
    path('editors/give_role/<int:pk>/', give_editor_role, name='give_editor_role'),

    path('regions/', regions_list, name='regions'),
    path('regions/create/', create_region, name='create_region'),
    path('regions/edit/<int:pk>/', edit_region, name='edit_region'),
    path('regions/delete/<int:pk>/', delete_region, name='delete_region'),

    path('genders/', genders_list, name='genders'),
    path('genders/create/', create_gender, name='create_gender'),
    path('genders/edit/<int:pk>/', edit_gender, name='edit_gender'),
    path('genders/delete/<int:pk>/', delete_gender, name='delete_gender'),

    path('menus/', menus_list, name='menus'),
    path('menus/create/', create_menu, name='create_menu'),
    path('menus/edit/<int:pk>/', edit_menu, name='edit_menu'),
    path('menus/delete/<int:pk>/', delete_menu, name='delete_menu'),

    path('roles/', roles_list, name='roles'),
    path('roles/create/', create_role, name='create_role'),
    path('roles/edit/<int:pk>/', edit_role, name='edit_role'),
    path('roles/delete/<int:pk>/', delete_role, name='delete_role'),

    path('scientific_degrees/', scientific_degrees_list, name='scientific_degrees'),
    path('scientific_degrees/create/', create_scientific_degree, name='create_scientific_degree'),
    path('scientific_degrees/edit/<int:pk>/', edit_scientific_degree, name='edit_scientific_degree'),
    path('scientific_degrees/delete/<int:pk>/', delete_scientific_degree, name='delete_scientific_degree'),

    path('users/', users_list, name='users'),
    path('users/view/<int:pk>/', view_user, name='view_user'),
    path('users/edit/<int:pk>/', edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', delete_user, name='delete_user'),

    path('permission_for_expertise_dashboard/', permission_for_expertise_dashboard, name='permission_for_expertise_dashboard'),

    path('change_password/', change_password, name='change_password'),


    # path('password_reset/', password_reset, name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user_app/register/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="user_app/register/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user_app/register/password_reset_complete.html'),
         name='password_reset_complete'),
]
