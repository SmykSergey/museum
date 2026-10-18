"""Переводимые поля библиотеки."""

from modeltranslation.translator import TranslationOptions, register

from .models import LibraryIssue


@register(LibraryIssue)
class LibraryIssueTranslationOptions(TranslationOptions):
    fields = ('title',)
