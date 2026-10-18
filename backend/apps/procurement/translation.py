"""Переводимые поля закупок."""

from modeltranslation.translator import TranslationOptions, register

from .models import ProcurementDocument


@register(ProcurementDocument)
class ProcurementDocumentTranslationOptions(TranslationOptions):
    fields = ('title',)
