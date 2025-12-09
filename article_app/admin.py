from django.contrib import admin
from article_app.models import *
from import_export.admin import ImportExportActionModelAdmin


@admin.register(Section)
class SectionAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name']


@admin.register(ArticleLanguage)
class ArticleLanguageAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name', 'key', 'status']


@admin.register(Stage)
class StageAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name']


@admin.register(ArticleStatus)
class ArticleStatusAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name', 'stage']


@admin.register(Article)
class ArticleAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'section', 'author', 'file', 'title', 'abstract', 'keywords', 'article_status',
                    'is_publish', 'created_at', 'updated_at']


@admin.register(ArticleFile)
class ArticleFileAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'article', 'file', 'file_name',
                    'file_size', 'file_type', 'file_status', 'created_at']


@admin.register(ExtraAuthor)
class ExtraAuthorAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'lname', 'fname', 'mname', 'email', 'work']


@admin.register(NotificationStatus)
class NotificationStatusAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name']


@admin.register(Notification)
class NotificationAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'article', 'from_user', 'to_user', 'message', 'notification_status',
                    'created_at']
