"""Собирает папку киоска из данных сайта.

    python manage.py build_kiosk                    # в dist/kiosk
    python manage.py build_kiosk --out /media/tablet/kiosk
    python manage.py build_kiosk --photos original  # без сжатия
    python manage.py build_kiosk --clean            # удалить старую сборку
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.kiosk.builder import KioskBuilder


class Command(BaseCommand):
    help = 'Собирает офлайн-бандл киоска (страницы, фото, data.json)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--out', default=str(Path(settings.BASE_DIR).parent / 'dist' / 'kiosk'),
            help='Папка для сборки',
        )
        parser.add_argument(
            '--photos', default='optimized', choices=['optimized', 'original'],
            help='Сжимать фото под экран стола или копировать как есть',
        )
        parser.add_argument('--max-size', type=int, default=1400,
                            help='Максимальная сторона фото при сжатии, px')
        parser.add_argument('--quality', type=int, default=82,
                            help='Качество JPEG при сжатии')
        parser.add_argument('--clean', action='store_true',
                            help='Удалить папку сборки перед началом')
        parser.add_argument('--no-legacy', action='store_true',
                            help='Не включать раздел 2014–2021 (папка old, ~111 МБ)')
        parser.add_argument('--zip', action='store_true',
                            help='Дополнительно упаковать сборку в архив рядом с папкой')

    def handle(self, *args, **options):
        out = Path(options['out'])

        if options['clean'] and out.exists():
            shutil.rmtree(out)
            self.stdout.write('Старая сборка удалена: %s' % out)

        self.stdout.write('Сборка киоска → %s' % out)
        self.stdout.write('Фото: %s' % options['photos'])
        self.stdout.write('')

        builder = KioskBuilder(
            out_dir=out,
            photos=options['photos'],
            max_size=options['max_size'],
            quality=options['quality'],
            with_legacy=not options['no_legacy'],
            verbose=self.stdout.write,
        )
        stats = builder.build()

        total = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Готово:'))
        self.stdout.write('  героев: %s' % stats['heroes'])
        self.stdout.write('  фото скопировано: %s (уже было: %s)' % (stats['photos'], stats['skipped']))
        self.stdout.write('  файлов в сборке: %s' % stats['files'])
        self.stdout.write('  размер: %.1f МБ' % (total / 1048576))
        if stats.get('broken_links'):
            self.stdout.write(self.style.WARNING(
                '  битых локальных ссылок: %s' % stats['broken_links']))
            for line in stats.get('missing_links', [])[:10]:
                self.stdout.write('    %s' % line)
        else:
            self.stdout.write('  битых ссылок нет')

        if options['zip']:
            import zipfile

            archive = out.with_suffix('.zip')
            self.stdout.write('')
            self.stdout.write('Упаковка в %s ...' % archive)
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for path in sorted(out.rglob('*')):
                    if path.is_file():
                        zf.write(path, path.relative_to(out).as_posix())
            self.stdout.write('  архив: %.1f МБ' % (archive.stat().st_size / 1048576))
        self.stdout.write('  папка: %s' % out)
