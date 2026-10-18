"""Админка страниц «Про музей» и «Історія музею»."""

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import AboutPage, HistoryPage


@admin.register(AboutPage)
class AboutPageAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ('Заголовок', {'fields': ('title', 'subtitle')}),
        ('Фото та текст', {'fields': ('photo', 'intro')}),
        ('Контакти', {
            'fields': ('main_location', 'map_embed_url'),
            'description': 'Графік роботи, адреса та ціни беруться з обраної локації.',
        }),
    )

    def has_add_permission(self, request):
        # страница всегда одна — добавить вторую нельзя
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistoryPage)
class HistoryPageAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ('Заголовок', {'fields': ('title',)}),
        ('Текст', {'fields': ('body',)}),
        ('Фото', {'fields': ('photo_1', 'photo_2')}),
    )

    def has_add_permission(self, request):
        return not HistoryPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
