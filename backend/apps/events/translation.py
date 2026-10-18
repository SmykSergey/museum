"""Переводимые поля событий."""

from modeltranslation.translator import TranslationOptions, register

from .models import Event


@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'summary', 'body')
