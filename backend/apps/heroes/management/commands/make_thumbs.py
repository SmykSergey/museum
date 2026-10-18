"""Создаёт миниатюры для фотографий героев.

Миниатюра делается автоматически при загрузке через админку. Эта команда
нужна для фото, загруженных раньше, и для повторной генерации.

    python manage.py make_thumbs            # только отсутствующие
    python manage.py make_thumbs --force    # пересоздать все
    python manage.py make_thumbs --size 300 --quality 78
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.images import make_thumbnail, thumbnail_filename
from apps.heroes.models import HeroPhoto


class Command(BaseCommand):
    help = 'Создаёт уменьшенные копии фото героев для карточек списков'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Пересоздать существующие миниатюры')
        parser.add_argument('--size', type=int, default=400,
                            help='Максимальная сторона миниатюры, px')
        parser.add_argument('--quality', type=int, default=80,
                            help='Качество JPEG миниатюры')

    def handle(self, *args, **options):
        force = options['force']
        photos = HeroPhoto.objects.all()

        created = skipped = failed = 0
        total = photos.count()
        self.stdout.write('Фото в базе: %s' % total)

        for index, photo in enumerate(photos.iterator(), start=1):
            if photo.thumb and not force:
                skipped += 1
                continue

            try:
                content = make_thumbnail(
                    photo.image,
                    max_size=options['size'],
                    quality=options['quality'],
                )
            except Exception as error:  # noqa: BLE001 — битый файл
                failed += 1
                self.stderr.write('  ! %s: %s' % (photo.image.name, error))
                continue

            if force:
                # перезаписываем файл на месте
                photo.thumb.storage.delete(photo.thumb.name)
                photo.thumb.name = ''

            photo.thumb.save(
                thumbnail_filename(photo.image.name), content, save=False,
            )
            photo.save(update_fields=['thumb'])
            created += 1

            if index % 100 == 0:
                self.stdout.write('  ... обработано %s из %s' % (index, total))

        total_size = sum(
            p.thumb.size for p in HeroPhoto.objects.exclude(thumb='') if p.thumb
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Готово:'))
        self.stdout.write('  создано миниатюр: %s' % created)
        self.stdout.write('  уже были: %s' % skipped)
        self.stdout.write('  ошибок: %s' % failed)
        self.stdout.write('  размер миниатюр: %.1f МБ' % (total_size / 1048576))
