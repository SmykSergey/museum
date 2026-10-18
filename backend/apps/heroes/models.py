"""Модели раздела «Герої не вмирають».

Данные перенесены из статического frontend/heroes-data.json (310 записей).
"""

import uuid

from django.db import models
from django.urls import reverse

from apps.core.utils import make_sort_key, transliterated_slug


class Branch(models.Model):
    """Рід військ / відомство: ЗСУ, прикордонна служба, Нацгвардія и т. д."""

    name = models.CharField('назва', max_length=200, unique=True)
    order = models.PositiveSmallIntegerField(
        'порядок виводу', default=100,
        help_text='Менше число — вище у списках.',
    )

    class Meta:
        verbose_name = 'рід військ'
        verbose_name_plural = 'роди військ'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name


def hero_thumb_path(instance, filename):
    """media/heroes/<slug>/thumbs/<имя>.jpg"""
    slug = instance.hero.slug or 'hero'
    return 'heroes/%s/thumbs/%s' % (slug, filename)


def hero_photo_path(instance, filename):
    """media/heroes/<slug героя>/<имя файла>"""
    slug = instance.hero.slug or 'hero'
    return 'heroes/%s/%s' % (slug, filename)


class Hero(models.Model):
    """Погибший защитник Украины."""

    class Period(models.TextChoices):
        ATO = '2014', '2014–2021 · АТО / ООС'
        INVASION = '2022', '2022 – .... · Повномасштабне вторгнення'

    slug = models.SlugField(
        'ідентифікатор', max_length=200, unique=True, blank=True,
        help_text='Латиницею, використовується в адресі сторінки. '
                  'Можна залишити порожнім — згенерується з ПІБ автоматично.',
    )
    full_name = models.CharField('ПІБ', max_length=250, db_index=True)
    rank_dates = models.CharField(
        'звання та дати', max_length=200, blank=True,
        help_text='Например: (06.08.1982 – 26.07.2023). Не перекладається.',
    )
    period = models.CharField(
        'період', max_length=4, choices=Period.choices,
        default=Period.INVASION, db_index=True,
        help_text='До якого періоду належить запис.',
    )
    branch = models.ForeignKey(
        Branch, verbose_name='рід військ', null=True, blank=True,
        on_delete=models.PROTECT, related_name='heroes',
    )
    birth_raion = models.CharField(
        'район Одещини', max_length=150, blank=True, db_index=True,
    )
    biography = models.TextField(
        'біографія', blank=True,
        help_text='Кожен абзац — з нового рядка (порожній рядок між абзацами).',
    )
    is_published = models.BooleanField(
        'опубліковано', default=True,
        help_text='Зніміть галочку, щоб приховати запис із сайту.',
    )

    # служебные поля для правильной украинской сортировки
    sort_key = models.CharField(
        'ключ сортування', max_length=500, blank=True, editable=False, db_index=True,
    )

    created_at = models.DateTimeField('створено', auto_now_add=True)
    updated_at = models.DateTimeField('оновлено', auto_now=True)

    class Meta:
        verbose_name = 'герой'
        verbose_name_plural = 'герої'
        ordering = ('sort_key', 'full_name')
        indexes = [models.Index(fields=['is_published', 'sort_key'])]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # sort_key строим всегда из украинского написания имени
        uk_name = getattr(self, 'full_name_uk', None) or self.full_name
        self.sort_key = make_sort_key(uk_name)

        # адрес страницы: если не задан вручную — транслитерируем ПІБ
        if not self.slug:
            self.slug = transliterated_slug(self, uk_name) or uuid.uuid4().hex[:12]

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('heroes:detail', kwargs={'slug': self.slug})

    @property
    def first_letter(self):
        """Первая буква фамилии — для группировки и алфавитного указателя."""
        name = (self.full_name or '').strip()
        return name[0].upper() if name else '?'

    @property
    def main_photo(self):
        """Главное фото карточки — первое по порядку."""
        photos = list(self.photos.all())
        return photos[0] if photos else None

    @property
    def gallery(self):
        """Все фото, кроме главного."""
        return list(self.photos.all())[1:]

    @property
    def biography_paragraphs(self):
        """Биография, разбитая на абзацы."""
        return [p.strip() for p in (self.biography or '').split('\n') if p.strip()]


class HeroPhoto(models.Model):
    """Фотография героя. Первая по порядку — главная (в карточке списка)."""

    hero = models.ForeignKey(
        Hero, verbose_name='герой', on_delete=models.CASCADE, related_name='photos',
    )
    image = models.ImageField('фото', upload_to=hero_photo_path)
    thumb = models.ImageField(
        'мініатюра', upload_to=hero_thumb_path, blank=True, editable=False,
        help_text='Створюється автоматично: зменшена копія для карток списків.',
    )
    caption = models.CharField('підпис', max_length=250, blank=True)
    order = models.PositiveSmallIntegerField(
        'порядок', default=0,
        help_text='Найменший порядок = головне фото картки.',
    )

    class Meta:
        verbose_name = 'фото героя'
        verbose_name_plural = 'фото героя'
        ordering = ('order', 'id')

    def __str__(self):
        return self.caption or ('Фото #%s' % self.pk)

    def save(self, *args, **kwargs):
        if self.image and not self.thumb:
            self._build_thumb()
        super().save(*args, **kwargs)

    def _build_thumb(self):
        """Делает миниатюру 400 px для карточек списков."""
        from apps.core.images import make_thumbnail, thumbnail_filename

        try:
            content = make_thumbnail(self.image)
        except Exception:  # noqa: BLE001 — битый файл не должен ломать сохранение
            return

        self.thumb.save(thumbnail_filename(self.image.name), content, save=False)

    @property
    def thumb_url(self):
        """URL миниатюры, а если её нет — исходного фото."""
        return self.thumb.url if self.thumb else self.image.url
