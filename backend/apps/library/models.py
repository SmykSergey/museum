"""Модели библиотеки музея (випуски «Вісника»)."""

from django.db import models


class LibraryIssue(models.Model):
    """Випуск періодичного видання музею."""

    number = models.PositiveIntegerField(
        'номер випуску', unique=True,
        help_text='Порядковий номер. За ним випуски сортуються.',
    )
    title = models.CharField(
        'назва', max_length=250, blank=True,
        help_text='Якщо порожньо — показується «Вісник музею».',
    )
    published_at = models.DateField(
        'дата випуску', null=True, blank=True,
    )
    file = models.FileField(
        'файл', upload_to='library/', blank=True,
        help_text='PDF або інший файл випуску.',
    )
    external_url = models.URLField(
        'зовнішнє посилання', blank=True,
        help_text='Якщо файл лежить на іншому сайті — вкажіть посилання.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб приховати випуск із сайту.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)

    class Meta:
        verbose_name = 'випуск бібліотеки'
        verbose_name_plural = 'бібліотека (випуски)'
        ordering = ('-number',)

    def __str__(self):
        return 'Випуск %s' % self.number

    @property
    def download_url(self):
        """Ссылка на файл: загруженный файл или внешний адрес."""
        if self.file:
            return self.file.url
        return self.external_url or ''

    @property
    def display_title(self):
        return self.title or 'Вісник музею'
