"""Переводимые поля экспонатов."""

from modeltranslation.translator import TranslationOptions, register

from .models import Exhibit


@register(Exhibit)
class ExhibitTranslationOptions(TranslationOptions):
    fields = ('title', 'summary', 'body')
