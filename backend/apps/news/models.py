"""Модели новостей музея."""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.utils import transliterated_slug


class NewsQuerySet(models.QuerySet):
    def published(self):
        """Только то, что можно показывать на сайте."""
        return self.filter(is_published=True)

    def recent(self):
        """Свежие новости первыми."""
        return self.published().order_by('-published_at', '-id')


class NewsItem(models.Model):
    """Новость: карточка на главной и отдельная страница."""

    slug = models.SlugField(
        'ідентифікатор', max_length=200, unique=True, blank=True,
        help_text='Латиницею, використовується в адресі сторінки. '
                  'Можна залишити порожнім — згенерується із заголовка автоматично.',
    )
    title = models.CharField('заголовок', max_length=300)
    summary = models.TextField(
        'короткий опис', blank=True, max_length=500,
        help_text='Показується в картці на головній сторінці.',
    )
    body = CKEditor5Field(
        'текст новини', blank=True, config_name='default',
        help_text='Повний текст для сторінки новини.',
    )
    photo = models.ImageField(
        'фото', upload_to='news/', blank=True,
        help_text='Використовується в картці новини.',
    )
    published_at = models.DateTimeField(
        'дата публікації', default=timezone.now,
        help_text='За цією датою новини сортуються.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб підготувати новину заздалегідь.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)
    updated_at = models.DateTimeField('оновлено', auto_now=True)

    objects = NewsQuerySet.as_manager()

    class Meta:
        verbose_name = 'новина'
        verbose_name_plural = 'новини'
        ordering = ('-published_at', '-id')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            title = getattr(self, 'title_uk', None) or self.title
            self.slug = transliterated_slug(self, title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})
