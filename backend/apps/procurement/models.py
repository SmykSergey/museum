"""Модели раздела «Державні закупівлі»."""

from django.db import models


class ProcurementDocument(models.Model):
    """Документ о закупках: план, изменения, обоснование."""

    date = models.DateField(
        'дата документа',
        help_text='За цією датою документи групуються за роками.',
    )
    title = models.CharField('назва документа', max_length=400)
    file = models.FileField(
        'файл', upload_to='procurement/', blank=True,
        help_text='PDF або інший файл документа.',
    )
    external_url = models.URLField(
        'зовнішнє посилання', blank=True,
        help_text='Якщо документ лежить на іншому сайті — вкажіть посилання.',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб приховати документ із сайту.',
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)

    class Meta:
        verbose_name = 'документ закупівлі'
        verbose_name_plural = 'державні закупівлі'
        ordering = ('-date', '-id')

    def __str__(self):
        return self.title

    @property
    def year(self):
        return self.date.year

    @property
    def download_url(self):
        if self.file:
            return self.file.url
        return self.external_url or ''
