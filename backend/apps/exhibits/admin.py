"""Админка экспонатов."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Exhibit


@admin.register(Exhibit)
class ExhibitAdmin(TabbedTranslationAdmin):
    list_display = ('preview', 'title', 'order', 'is_published')
    list_display_links = ('preview', 'title')
    list_editable = ('order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'summary', 'body')
    save_on_top = True

    fieldsets = (
        ('Основне', {'fields': ('slug', 'title', 'summary', 'order', 'is_published')}),
        ('Опис', {'fields': ('body',)}),
        ('Фото', {'fields': ('image',)}),
    )

    @admin.display(description='')
    def preview(self, obj):
        if not obj.image:
            return 'немає фото'
        return format_html(
            '<img src="{}" style="height:48px;width:64px;border-radius:4px;'
            'object-fit:cover;display:block;">',
            obj.image.url,
        )
