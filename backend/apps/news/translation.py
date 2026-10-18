"""Переводимые поля новостей."""

from modeltranslation.translator import TranslationOptions, register

from .models import NewsItem


@register(NewsItem)
class NewsItemTranslationOptions(TranslationOptions):
    fields = ('title', 'summary', 'body')
