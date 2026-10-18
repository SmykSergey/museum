"""Модели экспонатов (раздел «Експозиція»)."""

from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.utils import transliterated_slug


class Exhibit(models.Model):
    """Экспонат музея: карточка в разделе «Експозиція» и отдельная страница."""

    slug = models.SlugField(
        'ідентифікатор', max_length=200, unique=True, blank=True,
        help_text='Латиницею, використовується в адресі сторінки. '
                  'Можна залишити порожнім — згенерується з назви автоматично.',
    )
    title = models.CharField('назва', max_length=300)
    summary = models.TextField(
        'короткий опис', blank=True, max_length=500,
        help_text='Показується в картці на сторінці «Про музей».',
    )
    body = CKEditor5Field(
        'детальний опис', blank=True, config_name='default',
        help_text='Текст для сторінки експоната.',
    )
    image = models.ImageField(
        'фото', upload_to='exhibits/', blank=True,
        help_text='Використовується і в картці, і на сторінці експоната.',
    )
    order = models.PositiveSmallIntegerField(
        'порядок виводу', default=100,
        help_text='Менше число — вище у списку.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб приховати експонат із сайту.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)
    updated_at = models.DateTimeField('оновлено', auto_now=True)

    class Meta:
        verbose_name = 'експонат'
        verbose_name_plural = 'експонати'
        ordering = ('order', 'title')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            title = getattr(self, 'title_uk', None) or self.title
            self.slug = transliterated_slug(self, title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('exhibits:detail', kwargs={'slug': self.slug})
