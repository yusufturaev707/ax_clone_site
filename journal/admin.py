from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from journal.models import Journal, JournalYear


@admin.register(Journal)
class JournalAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'number', 'year', 'file_pdf', 'created_at', 'status', 'is_publish']


@admin.register(JournalYear)
class JournalYearAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'year', 'year_img', 'status']