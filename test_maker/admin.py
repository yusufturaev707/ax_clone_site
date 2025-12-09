from django.contrib import admin

from test_maker.models import Subject


# Register your models here.

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'picture', 'is_lang', 'lang_key', 'key', 'status']
