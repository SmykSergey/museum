"""Админка библиотеки."""

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import LibraryIssue


@admin.register(LibraryIssue)
class LibraryIssueAdmin(TabbedTranslationAdmin):
    list_display = ('number', 'title', 'published_at', 'has_file', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'number')
    ordering = ('-number',)

    @admin.display(description='файл', boolean=True)
    def has_file(self, obj):
        return bool(obj.file or obj.external_url)
