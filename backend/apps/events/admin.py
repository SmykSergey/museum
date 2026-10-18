"""Админка событий."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Event


@admin.register(Event)
class EventAdmin(TabbedTranslationAdmin):
    list_display = ('preview', 'title', 'starts_at', 'location', 'state', 'is_published')
    list_display_links = ('preview', 'title')
    list_editable = ('is_published',)
    list_filter = ('is_archived', 'is_published', 'location')
    search_fields = ('title', 'summary', 'body')
    date_hierarchy = 'starts_at'
    autocomplete_fields = ('location',)
    save_on_top = True

    fieldsets = (
        ('Основне', {
            'fields': ('slug', 'title', 'summary', 'location', 'is_published', 'is_archived'),
        }),
        ('Коли', {
            'fields': ('starts_at', 'ends_at'),
            'description': 'Подія автоматично потрапляє в архів після дати початку.',
        }),
        ('Детальний опис', {
            'fields': ('body',),
        }),
        ('Фото', {
            'fields': ('photo',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('location')

    @admin.display(description='')
    def preview(self, obj):
        if not obj.photo:
            return 'немає фото'
        return format_html(
            '<img src="{}" style="height:48px;width:64px;border-radius:4px;'
            'object-fit:cover;display:block;">',
            obj.photo.url,
        )

    @admin.display(description='стан')
    def state(self, obj):
        if obj.is_archived:
            return 'у архіві'
        return 'минула' if obj.is_past else 'актуальна'
