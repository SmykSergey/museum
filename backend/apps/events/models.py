"""Модели событий музея."""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.utils import transliterated_slug


class EventQuerySet(models.QuerySet):
    """Выборки событий.

    Архив считается по двум признакам: дата события уже прошла ИЛИ редактор
    вручную поставил галочку «в архіві» (например, событие отменили).
    """

    def published(self):
        return self.filter(is_published=True)

    def upcoming(self):
        """Актуальные события: ещё не прошли и не отправлены в архив."""
        return (
            self.published()
            .filter(is_archived=False, starts_at__gte=timezone.now())
            .order_by('starts_at', 'id')
        )

    def archive(self):
        """Прошедшие события и то, что редактор убрал в архив."""
        return (
            self.published()
            .filter(models.Q(is_archived=True) | models.Q(starts_at__lt=timezone.now()))
            .order_by('-starts_at', '-id')
        )


class Event(models.Model):
    """Событие музея: выставка, экскурсия, встреча."""

    slug = models.SlugField(
        'ідентифікатор', max_length=200, unique=True, blank=True,
        help_text='Латиницею, використовується в адресі сторінки. '
                  'Можна залишити порожнім — згенерується із заголовка автоматично.',
    )
    title = models.CharField('назва', max_length=300)
    summary = models.TextField(
        'короткий опис', blank=True, max_length=500,
        help_text='Показується в картці події.',
    )
    body = CKEditor5Field(
        'детальний опис', blank=True, config_name='default',
        help_text='Повний текст для сторінки події.',
    )
    photo = models.ImageField(
        'фото', upload_to='events/', blank=True,
        help_text='Використовується в картці події.',
    )
    starts_at = models.DateTimeField(
        'дата і час початку',
        help_text='Після цієї дати подія автоматично переходить у архів.',
    )
    ends_at = models.DateTimeField(
        'дата і час завершення', null=True, blank=True,
        help_text='Заповнювати не обов’язково.',
    )
    location = models.ForeignKey(
        'locations.Location', verbose_name='локація', null=True, blank=True,
        on_delete=models.PROTECT, related_name='events',
        help_text='Де саме відбудеться подія.',
    )
    is_archived = models.BooleanField(
        'в архіві', default=False,
        help_text='Позначте, щоб достроково прибрати подію в архів.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб підготувати подію заздалегідь.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)
    updated_at = models.DateTimeField('оновлено', auto_now=True)

    objects = EventQuerySet.as_manager()

    class Meta:
        verbose_name = 'подія'
        verbose_name_plural = 'події'
        ordering = ('-starts_at', '-id')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            title = getattr(self, 'title_uk', None) or self.title
            self.slug = transliterated_slug(self, title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'slug': self.slug})

    @property
    def is_past(self):
        return self.starts_at < timezone.now()
