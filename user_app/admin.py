from django.contrib import admin
from django.contrib.auth.models import Permission
from import_export.admin import ImportExportActionModelAdmin
from modeltranslation.admin import TranslationAdmin

from user_app.models import *


@admin.register(Permission)
class PermissionAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'name', 'content_type', 'codename']


@admin.register(Region)
class RegionAdmin(ImportExportActionModelAdmin, TranslationAdmin):
    list_display = ['id', 'name']

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Gender)
class GenderAdmin(ImportExportActionModelAdmin, TranslationAdmin):
    list_display = ['id', 'name']

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Role)
class RoleAdmin(ImportExportActionModelAdmin, TranslationAdmin):
    list_display = ['id', 'name']
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(Menu)
class MenuAdmin(ImportExportActionModelAdmin, TranslationAdmin):
    list_display = ['id', 'name', 'status',
                    'url', 'url_name', 'icon_name', 'order', 'get_roles']
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@admin.register(User)
class UserAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'username', 'last_name', 'first_name', 'middle_name', 'birthday', 'gender', 'avatar', 'email',
                    'phone', 'pser', 'pnum', 'region', 'work', 'get_roles', 'created_at', 'updated_at']


@admin.register(Editor)
class EditorAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'user']


@admin.register(Reviewer)
class ReviewerAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'user', 'scientific_degree', 'is_reviewer', 'created_at', 'updated_at']
