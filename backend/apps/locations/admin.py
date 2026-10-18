"""Админка локаций."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Location


@admin.register(Location)
class LocationAdmin(TabbedTranslationAdmin):
    list_display = ('preview', 'name', 'address', 'order', 'events_count', 'is_published')
    list_display_links = ('preview', 'name')
    list_editable = ('order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name', 'address', 'description')
    save_on_top = True

    fieldsets = (
        ('Основне', {
            'fields': ('slug', 'name', 'address', 'order', 'is_published'),
        }),
        ('Відвідувачам', {
            'fields': ('schedule', 'prices'),
        }),
        ('Опис', {
            'fields': ('description',),
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

    @admin.display(description='подій')
    def events_count(self, obj):
        return obj.events.count()
