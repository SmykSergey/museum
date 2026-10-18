"""Страницы с редактируемым содержимым: «Про музей» и «Історія музею».

Обе страницы существуют в единственном экземпляре, поэтому модели сделаны
singleton: в таблице всегда одна запись с pk=1, а редактируются они
в админке как обычные объекты.
"""

from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class SingletonModel(models.Model):
    """Модель, у которой может быть только одна запись."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # удалять единственную страницу нельзя — иначе админка упадёт на пустой таблице
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutPage(SingletonModel):
    """Страница «Про музей»."""

    title = models.CharField('заголовок', max_length=200, default='Про музей')
    subtitle = models.CharField('підзаголовок', max_length=250, blank=True)
    photo = models.ImageField(
        'головне фото', upload_to='pages/', blank=True,
        help_text='Фото будівлі музею.',
    )
    intro = CKEditor5Field(
        'вступний текст', blank=True, config_name='default',
        help_text='Необов’язковий текст над картками.',
    )
    main_location = models.ForeignKey(
        'locations.Location', verbose_name='головна локація', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text='Звідси беруться графік роботи, адреса та ціни на квитки.',
    )
    map_embed_url = models.URLField(
        'посилання на карту', blank=True, max_length=1000,
        help_text='Адреса з атрибута src у Google Maps (iframe). '
                  'Наприклад: https://www.google.com/maps/embed?pb=...',
    )

    class Meta:
        verbose_name = 'сторінка «Про музей»'
        verbose_name_plural = 'сторінка «Про музей»'

    def __str__(self):
        return self.title


class HistoryPage(SingletonModel):
    """Страница «Історія музею»."""

    title = models.CharField('заголовок', max_length=200, default='Історія музею')
    body = CKEditor5Field(
        'текст', blank=True, config_name='default',
        help_text='Основна розповідь про історію музею.',
    )
    photo_1 = models.ImageField(
        'фото 1', upload_to='pages/', blank=True,
        help_text='Ліва колонка, верхнє зображення.',
    )
    photo_2 = models.ImageField(
        'фото 2', upload_to='pages/', blank=True,
        help_text='Ліва колонка, нижнє зображення.',
    )

    class Meta:
        verbose_name = 'сторінка «Історія музею»'
        verbose_name_plural = 'сторінка «Історія музею»'

    def __str__(self):
        return self.title

    @property
    def photos(self):
        return [photo for photo in (self.photo_1, self.photo_2) if photo]
