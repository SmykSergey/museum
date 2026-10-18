"""Админка раздела «Державні закупівлі»."""

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import ProcurementDocument


@admin.register(ProcurementDocument)
class ProcurementDocumentAdmin(TabbedTranslationAdmin):
    list_display = ('date', 'title', 'has_file', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'date')
    search_fields = ('title',)
    date_hierarchy = 'date'
    ordering = ('-date',)

    @admin.display(description='файл', boolean=True)
    def has_file(self, obj):
        return bool(obj.file or obj.external_url)
