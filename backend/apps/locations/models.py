"""Модели локаций музея.

Локации — это четыре площадки: Одеський історико-краєзнавчий музей,
Музей «Степова Україна», Меморіал 411-ї батареї та Болградський музей.
"""

from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.utils import transliterated_slug


class Location(models.Model):
    """Площадка музея: адрес, график работы, цены."""

    slug = models.SlugField(
        'ідентифікатор', max_length=200, unique=True, blank=True,
        help_text='Латиницею, використовується в адресі сторінки. '
                  'Можна залишити порожнім — згенерується з назви автоматично.',
    )
    name = models.CharField('назва', max_length=250)
    address = models.CharField(
        'адреса', max_length=250, blank=True,
        help_text='Наприклад: вул. Гаванна, 4.',
    )
    schedule = models.TextField(
        'графік роботи', blank=True,
        help_text='Кожен рядок — окремий пункт, наприклад «Пн-Пт: 10:00 – 18:00».',
    )
    prices = CKEditor5Field(
        'ціни на квитки', blank=True, config_name='default',
        help_text='Довільний текст із форматуванням.',
    )
    description = CKEditor5Field(
        'опис локації', blank=True, config_name='default',
        help_text='Текст для сторінки локації.',
    )
    photo = models.ImageField(
        'фото', upload_to='locations/', blank=True,
        help_text='Використовується в картці локації на головній сторінці.',
    )
    order = models.PositiveSmallIntegerField(
        'порядок виводу', default=100,
        help_text='Менше число — вище у списках.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб приховати локацію із сайту.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)
    updated_at = models.DateTimeField('оновлено', auto_now=True)

    class Meta:
        verbose_name = 'локація'
        verbose_name_plural = 'локації'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            name = getattr(self, 'name_uk', None) or self.name
            self.slug = transliterated_slug(self, name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('locations:detail', kwargs={'slug': self.slug})

    @property
    def schedule_lines(self):
        """График работы, разбитый по строкам."""
        return [line.strip() for line in (self.schedule or '').split('\n') if line.strip()]
