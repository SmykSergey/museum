"""Переводимые поля страниц."""

from modeltranslation.translator import TranslationOptions, register

from .models import AboutPage, HistoryPage


@register(AboutPage)
class AboutPageTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'intro')


@register(HistoryPage)
class HistoryPageTranslationOptions(TranslationOptions):
    fields = ('title', 'body')
