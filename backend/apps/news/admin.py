"""Админка новостей."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(TabbedTranslationAdmin):
    list_display = ('preview', 'title', 'published_at', 'is_published')
    list_display_links = ('preview', 'title')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'summary', 'body')
    date_hierarchy = 'published_at'
    save_on_top = True

    fieldsets = (
        ('Основне', {
            'fields': ('slug', 'title', 'summary', 'published_at', 'is_published'),
        }),
        ('Текст новини', {
            'fields': ('body',),
        }),
        ('Фото', {
            'fields': ('photo',),
        }),
    )

    @admin.display(description='')
    def preview(self, obj):
        if not obj.photo:
            return 'немає фото'
        return format_html(
            '<img src="{}" style="height:48px;width:64px;border-radius:4px;'
            'object-fit:cover;display:block;">',
            obj.photo.url,
        )
