"""Регистрация переводимых полей для django-modeltranslation.

Украинский — основной язык (MODELTRANSLATION_DEFAULT_LANGUAGE = 'uk'),
английский заполняется вручную в админке (транслитерация имени + перевод биографии).
"""

from modeltranslation.translator import TranslationOptions, register

from .models import Branch, Hero


@register(Branch)
class BranchTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Hero)
class HeroTranslationOptions(TranslationOptions):
    fields = ('full_name', 'biography')
