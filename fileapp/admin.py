from django.contrib import admin
from fileapp.models import *


@admin.register(TemplateFile)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'template_file', 'code_name']