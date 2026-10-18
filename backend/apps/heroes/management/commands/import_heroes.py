"""Импорт раздела «Герої не вмирають» в базу данных.

Источники:
  * данные (ПІБ, биография, порядок фото) — apps/heroes/data/heroes-data.json,
    он хранится в репозитории;
  * сами файлы фото — внешний архив, который распаковывается в папку,
    указанную в --photos (по умолчанию ../frontend/heroes-photos).

Команда идемпотентна: повторный запуск обновляет записи по slug и пересобирает
галерею, дублей не создаёт.

    python manage.py import_heroes                  # полный импорт
    python manage.py import_heroes --dry-run        # только отчёт
    python manage.py import_heroes --photos /path/to/photos
    python manage.py import_heroes --skip-photos    # фото уже в media/, копировать нечего
    python manage.py import_heroes --heroes Ivanov_Valerii_Anatoliiovych
"""

import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.db import transaction

from apps.core.utils import transliterate_uk
from apps.heroes.models import Branch, Hero, HeroPhoto

def clean_name(name):
    """Убирает BOM и лишние пробелы из ПІБ.

    В файлах киоска 299 имён из 500 начинаются с невидимого BOM (U+FEFF) —
    без чистки ломается группировка по первым буквам и сортировка.
    """
    return (name or '').replace('\ufeff', '').strip()


SLUG_RE = re.compile(r'^[-a-zA-Z0-9_]+$')


def record_slug(record):
    """Slug записи: берём id, а если он не годится — транслитерируем ПІБ.

    В heroes.json нашлась запись, где вместо id лежит ПІБ кирилицею —
    такой slug нельзя использовать в адресе страницы.
    """
    raw = (record.get('id') or '').strip()
    if SLUG_RE.match(raw):
        return raw
    return slugify(transliterate_uk(clean_name(record.get('name')))) or ''


def photo_relative_path(value):
    """Приводит путь фото из любого формата к виду '<каталог>/<файл>'.

    Новый формат (heroes.json киоска): '../<рід військ>/<slug>/1.jpg'
    Старый формат (heroes-data.json): 'heroes-photos/<slug>/1.jpg'
    """
    path = Path((value or '').replace('\\', '/'))

    parts = [part for part in path.parts if part not in ('..', '.')]
    if parts and parts[0] == 'heroes-photos':
        parts = parts[1:]
    return Path(*parts) if parts else Path('')


# папка со свёрстанными фото (внешний архив), рядом с backend/
DEFAULT_PHOTOS_DIR = settings.BASE_DIR.parent / 'frontend' / 'heroes-photos'


class Command(BaseCommand):
    help = 'Импортирует героев из heroes-data.json и фото в media/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            default=str(settings.BASE_DIR / 'apps' / 'heroes' / 'data' / 'heroes-data.json'),
            help='Путь к heroes-data.json',
        )
        parser.add_argument(
            '--photos', default=str(DEFAULT_PHOTOS_DIR),
            help='Папка с фото героев (структура <id>/<номер>.jpg)',
        )
        parser.add_argument(
            '--heroes', nargs='*', default=None,
            help='Импортировать только указанные id (латиницей, как в JSON)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Показать, что будет сделано, ничего не записывая',
        )
        parser.add_argument(
            '--skip-photos', action='store_true',
            help='Не копировать файлы (считать, что они уже лежат в media/)',
        )
        parser.add_argument(
            '--period', default='2022', choices=['2014', '2022'],
            help='К какому периоду отнести записи (по умолчанию 2022)',
        )

    def handle(self, *args, **options):
        data_path = Path(options['data'])
        photos_root = Path(options['photos'])
        only_ids = options['heroes']
        dry_run = options['dry_run']
        skip_photos = options['skip_photos']

        if not data_path.exists():
            raise CommandError('Не найден файл данных: %s' % data_path)

        # Защита от потери данных: без папки с фото команда удалила бы
        # существующие записи HeroPhoto и не смогла бы создать новые.
        if not photos_root.exists() and not skip_photos:
            raise CommandError(
                'Папка с фото не найдена: %s\n'
                'Распакуйте архив с фото в эту папку или укажите --photos ПУТЬ.\n'
                'Если фото уже лежат в media/heroes/, добавьте --skip-photos.'
                % photos_root
            )

        with data_path.open(encoding='utf-8') as fh:
            records = json.load(fh)

        if only_ids:
            records = [r for r in records if r.get('id') in set(only_ids)]

        if not records:
            raise CommandError('Не найдено ни одной записи для импорта.')

        self.stdout.write('Данные: %s' % data_path)
        if not skip_photos:
            self.stdout.write('Фото:   %s' % photos_root)
        self.stdout.write('Записей к импорту: %s' % len(records))
        self.stdout.write('')

        created_heroes = updated_heroes = 0
        created_photos = copied_files = missing_files = missing_in_media = 0
        branches = {}

        for record in records:
            slug = record_slug(record)
            if not slug:
                self.stderr.write('  ! пропущена запись без id: %r' % record.get('name'))
                continue

            if dry_run:
                self.stdout.write('  [dry-run] %s — %s' % (slug, record['name']))
                continue

            with transaction.atomic():
                branch = None
                branch_name = (
                    record.get('military_branch') or record.get('branch') or ''
                ).strip()
                if branch_name:
                    if branch_name not in branches:
                        branches[branch_name], _ = Branch.objects.get_or_create(name=branch_name)
                    branch = branches[branch_name]

                hero, created = Hero.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'full_name': clean_name(record['name']),
                        'rank_dates': record.get('rank_dates') or '',
                        'period': options['period'],
                        'branch': branch,
                        'birth_raion': record.get('birth_raion') or '',
                        'biography': '\n\n'.join(
                            p.strip() for p in (record.get('details') or []) if p.strip()
                        ),
                        'is_published': True,
                    },
                )
                created_heroes += created
                updated_heroes += not created

                # Галерея пересобирается целиком — так команда остаётся идемпотентной.
                hero.photos.all().delete()

                # порядок: главное фото из JSON идёт первым
                main_photo = record.get('photo')
                gallery = list(record.get('gallery') or [])
                if main_photo and main_photo in gallery:
                    gallery.remove(main_photo)
                    gallery.insert(0, main_photo)

                for order, relative in enumerate(gallery):
                    inner = photo_relative_path(relative)
                    target_relative = 'heroes/%s/%s' % (slug, inner.name)

                    if skip_photos:
                        if not (Path(settings.MEDIA_ROOT) / target_relative).exists():
                            missing_in_media += 1
                    else:
                        source = photos_root / inner
                        if not source.exists():
                            missing_files += 1
                            self.stderr.write('  ! нет файла: %s' % source)
                            continue
                        target = Path(settings.MEDIA_ROOT) / target_relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        # файл мог остаться пустым от прерванного копирования —
                        # такой нужно перезаписать, а не считать готовым
                        if not target.exists() or target.stat().st_size == 0:
                            shutil.copy2(source, target)
                            copied_files += 1

                    HeroPhoto.objects.create(hero=hero, image=target_relative, order=order)
                    created_photos += 1

            if (created_heroes + updated_heroes) % 50 == 0:
                self.stdout.write('  ... обработано %s' % (created_heroes + updated_heroes))

        if dry_run:
            self.stdout.write(self.style.WARNING('Это был dry-run, база не изменена.'))
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Импорт завершён:'))
        self.stdout.write('  героев создано: %s' % created_heroes)
        self.stdout.write('  героев обновлено: %s' % updated_heroes)
        self.stdout.write('  родов войск: %s' % Branch.objects.count())
        self.stdout.write('  фото в базе: %s' % HeroPhoto.objects.count())
        if not skip_photos:
            self.stdout.write('  файлов скопировано: %s' % copied_files)
        if missing_files:
            self.stdout.write(self.style.WARNING('  файлов не найдено в архиве: %s' % missing_files))
        if missing_in_media:
            self.stdout.write(
                self.style.WARNING('  записей без файла в media/: %s' % missing_in_media)
            )
