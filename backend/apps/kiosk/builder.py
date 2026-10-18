"""Сборка офлайн-бандла для киоска из базы сайта.

Киоск — это сенсорный стол в музее, интернет там может пропадать, поэтому
он работает с локальной копией. Команда `build_kiosk` собирает папку,
которую достаточно целиком скопировать на стол:

    dist/kiosk/
    ├── index.html              заставка
    ├── portal.html             выбор периода
    ├── start_2022.html         выбор рода войск + карта
    ├── preview_<branch>.html   списки по родам войск
    ├── 2022/detail/*.html      карточки героев
    ├── 2022/<рід>/<slug>/*.jpg фото (ужатые)
    ├── maps/*.svg              карты районов
    ├── style.css
    ├── soldiers_data.js        данные для поиска и фильтра по району
    ├── data.json               полный набор данных (для синхронизации)
    └── sync.json               версия и манифест файлов
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from apps.heroes.constants import DISTRICT_MAPS, district_map_slug
from apps.heroes.models import Hero

# имя файла-списка для каждого рода войск (как в исходном макете киоска)
BRANCH_CODES = {
    'Збройні Сили України': 'zsu',
    'Державна прикордонна служба України': 'dpsu',
    'Національна гвардія України': 'guard',
    'Міністерство внутрішніх справ України': 'mvs',
    'Служба безпеки України': 'sbu',
    'Державна служба України з надзвичайних ситуацій': 'dsns',
    'Волонтерський рух': 'volunteers',
    'Добровольчі формування': 'dobrovoltsi',
}

DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1280, height=1024, initial-scale=1.0">
    <title>{name} - Меморіал</title>
    <link rel="stylesheet" href="../../style.css">
</head>
<body class="detail-page">
    <h1 class="banner-text">Герої не вмирають</h1>
    <a href="../../{back_link}" class="back-nav">ДО СПИСКУ</a>
{prev_link}
{next_link}
    <div class="container">
        <div class="bio-column">
            <div class="photo-frame"><img src="{main_photo}" alt="{name}"></div>
            <div class="bio-scroll-container">
                <div class="bio-scroll" id="bioScroll">
                    <h2 class="hero-name">{name}</h2>
                    <div class="hero-rank">{dates}</div>
                    <div class="hero-details">{details}</div>
                </div>
                <div class="scroll-controls">
                    <div class="scroll-btn" onclick="scrollText(-150)"><svg viewBox="0 0 24 24" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg></div>
                    <div class="scroll-btn" onclick="scrollText(150)"><svg viewBox="0 0 24 24" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg></div>
                </div>
            </div>
        </div>

        <div class="interactive-column">
            <div class="main-display" id="mainDisplay">
                <img src="{main_photo}" id="displayImage" alt="{name}">
            </div>

            <div class="gallery-wrapper">
                <div class="gallery-nav" onclick="scrollGallery(-300)"><svg viewBox="0 0 24 24" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg></div>
                <div class="gallery-box" id="galleryBox">{thumbs}</div>
                <div class="gallery-nav" onclick="scrollGallery(300)"><svg viewBox="0 0 24 24" fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg></div>
            </div>
        </div>
    </div>

    <script>
        function updateDisplay(src, label, el) {{
            const di = document.getElementById('displayImage');
            di.style.opacity = '0';
            setTimeout(() => {{ di.src = src; di.style.opacity = '1';
                document.querySelectorAll('.thumb').forEach(t => t.classList.remove('active'));
                el.classList.add('active');
            }}, 200);
        }}
        function scrollText(distance) {{ document.getElementById('bioScroll').scrollBy({{ top: distance, behavior: 'smooth' }}); }}
        function scrollGallery(distance) {{ document.getElementById('galleryBox').scrollBy({{ left: distance, behavior: 'smooth' }}); }}
    </script>
</body>
</html>
"""

PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1280, height=1024, initial-scale=1.0">
    <title>{title} - Меморіал</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="preview-page">
    <a href="start_2022.html" class="back-nav">НАЗАД</a>
    <div class="header"><h1 class="banner-text">Герої не вмирають</h1></div>
    <div class="list-wrap">
        <div class="heroes-grid" id="heroGrid">{cards}</div>
        <div class="preview-controls">
            <div class="prev-btn" onclick="scrollGrid(-450)"><svg viewBox="0 0 24 24" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg></div>
            <div class="prev-btn" onclick="scrollGrid(450)"><svg viewBox="0 0 24 24" fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg></div>
        </div>
    </div>
    <script>
        function scrollGrid(distance) {{ document.getElementById('heroGrid').scrollBy({{ top: distance, behavior: 'smooth' }}); }}
    </script>
</body>
</html>
"""


def branch_code(branch_name):
    """Имя ветки → имя файла списка (preview_<code>.html)."""
    name = (branch_name or '').strip()
    if name in BRANCH_CODES:
        return BRANCH_CODES[name]

    from apps.core.utils import transliterate_uk
    from django.utils.text import slugify

    return slugify(transliterate_uk(name)) or 'other'


def html_escape(value):
    return (
        str(value or '')
        .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def photo_url_for_detail(photo):
    """Путь к фото из папки 2022/detail/ → '../../media/...'."""
    return '../../' + photo


class KioskBuilder:
    """Собирает папку киоска из данных сайта."""

    def __init__(self, out_dir, photos='optimized', max_size=1400, quality=82,
                 with_legacy=True, verbose=None):
        self.out = Path(out_dir)
        self.photos_mode = photos
        self.max_size = max_size
        self.quality = quality
        self.with_legacy = with_legacy
        self.verbose = verbose or (lambda msg: None)
        self.stats = {'photos': 0, 'skipped': 0, 'heroes': 0, 'files': 0}

    # ---------- публичная точка входа ----------

    def build(self):
        heroes = list(
            Hero.objects
            .filter(is_published=True)
            .select_related('branch')
            .prefetch_related('photos')
            .order_by('sort_key', 'full_name')
        )

        self.out.mkdir(parents=True, exist_ok=True)
        self._copy_ui()
        self._copy_maps()
        self._write_heroes(heroes)
        self._write_indexes(heroes)
        self._write_data(heroes)
        self.stats['broken_links'] = self.check_links()
        return self.stats

    # ---------- статика ----------

    def _copy_ui(self):
        """Копирует готовые страницы киоска и стили, если они есть рядом."""
        source = Path(settings.KIOSK_DESIGN_DIR)
        if not source.exists():
            self.verbose('  ! папка макета киоска не найдена: %s' % source)
            return

        for name in ('index.html', 'portal.html', 'start_2022.html', 'style.css', 'style2.css'):
            src = source / name
            if src.exists():
                shutil.copy2(src, self.out / name)

        old_dir = source / 'old'
        if old_dir.exists() and self.with_legacy:
            # раздел 2014–2021 живёт пока в старом виде; --no-legacy убирает эти 111 МБ
            shutil.copytree(old_dir, self.out / 'old', dirs_exist_ok=True)

    def _copy_maps(self):
        """Карты районов + интерактивная карта области для start_2022.html."""
        maps_out = self.out / 'maps'
        maps_out.mkdir(exist_ok=True)

        design_maps = Path(settings.KIOSK_DESIGN_DIR) / 'maps'
        if design_maps.exists():
            # в макете лежит интерактивная карта районов — копируем папку целиком
            shutil.copytree(design_maps, maps_out, dirs_exist_ok=True)
            return

        static_maps = Path(settings.BASE_DIR) / 'static' / 'maps'
        for slug in DISTRICT_MAPS.values():
            src = static_maps / ('%s.svg' % slug)
            if src.exists():
                shutil.copy2(src, maps_out / ('%s.svg' % slug))

    # ---------- данные ----------

    def _photo_relative(self, photo):
        """Путь фото внутри бандла: 2022/<рід>/<slug>/<файл>."""
        slug = photo.hero.slug
        branch = photo.hero.branch.name if photo.hero.branch else 'Інші'
        return '2022/%s/%s/%s' % (branch, slug, Path(photo.image.name).name)

    def _existing_photo(self, photo):
        """Путь фото внутри бандла, если файл реально скопирован, иначе None."""
        if photo is None:
            return None
        rel = self._photo_relative(photo)
        return rel if (self.out / rel).exists() else None

    def _copy_photo(self, photo):
        target_rel = self._photo_relative(photo)
        target = self.out / target_rel
        if target.exists() and target.stat().st_size > 0:
            self.stats['skipped'] += 1
            return target_rel

        source = Path(settings.MEDIA_ROOT) / photo.image.name
        if not source.exists() or source.stat().st_size == 0:
            # битый или пустой файл — пропускаем, но не роняем всю сборку
            self.stats.setdefault('broken', 0)
            self.stats['broken'] += 1
            return None

        target.parent.mkdir(parents=True, exist_ok=True)

        if self.photos_mode == 'original':
            shutil.copy2(source, target)
        else:
            try:
                self._resize(source, target)
            except Exception as error:  # noqa: BLE001 — файл может быть битым
                self.stats.setdefault('broken', 0)
                self.stats['broken'] += 1
                self.verbose('  ! не удалось обработать %s: %s' % (source.name, error))
                shutil.copy2(source, target)

        self.stats['photos'] += 1
        return target_rel

    def _resize(self, source, target):
        """Уменьшает фото под экран стола (1280×1024) и сжимает."""
        from PIL import Image, ImageFile, ImageOps

        # часть фото в архиве слегка обрезана — PIL по умолчанию на таких падает,
        # а нам достаточно показать то, что читается
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        with Image.open(source) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            img.thumbnail((self.max_size, self.max_size), Image.LANCZOS)
            img.save(target, format='JPEG', quality=self.quality, optimize=True, progressive=True)

    def _write_heroes(self, heroes):
        """Генерирует карточку героя на каждого: 2022/detail/detail_<slug>.html."""
        no_photo_src = Path(settings.BASE_DIR) / 'static' / 'ph' / 'no-photo.jpg'
        no_photo_dst = self.out / '2022' / 'no-photo.jpg'
        if no_photo_src.exists() and not no_photo_dst.exists():
            no_photo_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(no_photo_src, no_photo_dst)
        detail_dir = self.out / '2022' / 'detail'
        detail_dir.mkdir(parents=True, exist_ok=True)

        by_id = {hero.slug: hero for hero in heroes}

        for index, hero in enumerate(heroes):
            photos = [self._copy_photo(photo) for photo in hero.photos.all()]
            photos = [p for p in photos if p]

            map_slug = district_map_slug(hero.birth_raion)
            gallery = list(photos)
            if map_slug:
                gallery.append('maps/%s.svg' % map_slug)

            main_photo = photos[0] if photos else '2022/no-photo.jpg'

            back = 'preview_%s.html' % branch_code(hero.branch.name if hero.branch else '')

            # соседи по списку — как в исходном макете (стрелки влево/вправо)
            prev_hero = heroes[index - 1] if index > 0 else None
            next_hero = heroes[index + 1] if index + 1 < len(heroes) else None

            prev_link = (
                '    <a href="detail_%s.html" class="nav-hero-btn nav-prev">%s</a>'
                % (prev_hero.slug, self._arrow('prev'))
                if prev_hero else ''
            )
            next_link = (
                '    <a href="detail_%s.html" class="nav-hero-btn nav-next">%s</a>'
                % (next_hero.slug, self._arrow('next'))
                if next_hero else ''
            )

            thumbs = ''.join(
                '<div class="thumb%s" onclick="updateDisplay(\'../../%s\', \'\', this)">'
                '<img src="../../%s"></div>' % (' active' if pos == 0 else '', src, src)
                for pos, src in enumerate(gallery)
            )

            details = ''.join('<p>%s</p>' % html_escape(p) for p in hero.biography_paragraphs)

            html = DETAIL_TEMPLATE.format(
                name=html_escape(hero.full_name),
                dates=html_escape(hero.rank_dates),
                details=details,
                main_photo='../../' + main_photo,
                back_link=back,
                prev_link=prev_link,
                next_link=next_link,
                thumbs=thumbs,
            )
            (detail_dir / ('detail_%s.html' % hero.slug)).write_text(html, encoding='utf-8')

        self.stats['heroes'] = len(heroes)

    @staticmethod
    def _arrow(direction):
        if direction == 'prev':
            points = '15 18 9 12 15 6'
        else:
            points = '9 18 15 12 9 6'
        return (
            '<svg viewBox="0 0 24 24" fill="none" stroke-width="3" stroke-linecap="round" '
            'stroke-linejoin="round"><polyline points="%s"></polyline></svg>' % points
        )

    def check_links(self):
        """Проверяет, что все локальные ссылки из HTML-страниц ведут на существующие файлы."""
        import re

        pattern = re.compile(r'(?:src|href)="([^"]+)"')
        missing = set()

        for page in self.out.rglob('*.html'):
            if 'old' in page.relative_to(self.out).parts:
                continue
            for value in pattern.findall(page.read_text(encoding='utf-8', errors='replace')):
                if value.startswith(('http://', 'https://', '#', 'mailto:', 'javascript:', 'data:')):
                    continue
                if '${' in value:
                    continue
                target = (page.parent / value.split('?')[0].split('#')[0]).resolve()
                if not target.exists():
                    missing.add('%s → %s' % (page.relative_to(self.out), value))

        self.stats['missing_links'] = sorted(missing)
        return len(missing)

    def _write_indexes(self, heroes):
        """Списки по родам войск + soldiers_data.js для поиска и карты."""
        by_branch = {}
        for hero in heroes:
            name = hero.branch.name if hero.branch else 'Інші'
            by_branch.setdefault(name, []).append(hero)

        for branch_name, branch_heroes in by_branch.items():
            cards = []
            for hero in branch_heroes:
                rel = self._existing_photo(hero.photos.first())
                cards.append(
                    '<a href="2022/detail/detail_%s.html" class="hero-card">'
                    '<div class="img-wrap"><img src="%s" loading="lazy"></div>'
                    '<div class="info"><div class="name">%s</div>'
                    '<div class="dates">%s</div></div></a>'
                    % (hero.slug, rel or '2022/no-photo.jpg',
                       html_escape(hero.full_name), html_escape(hero.rank_dates))
                )

            page = PREVIEW_TEMPLATE.format(
                title=html_escape(branch_name),
                cards=''.join(cards),
            )
            (self.out / ('preview_%s.html' % branch_code(branch_name))).write_text(
                page, encoding='utf-8',
            )

        soldiers = []
        for hero in heroes:
            rel = self._existing_photo(hero.photos.first())
            soldiers.append({
                'id': hero.slug,
                'name': hero.full_name,
                'dates': hero.rank_dates,
                'url': '2022/detail/detail_%s.html' % hero.slug,
                'photo': rel or '2022/no-photo.jpg',
                'birth_raion': hero.birth_raion or None,
                'period': hero.period,
                'branch': hero.branch.name if hero.branch else '',
            })

        content = 'const SOLDIERS_DATA = ' + json.dumps(
            soldiers, ensure_ascii=False, indent=1,
        ) + ';\n'
        (self.out / 'soldiers_data.js').write_text(content, encoding='utf-8')

    def _write_data(self, heroes):
        """data.json + sync.json — то, по чему киоск понимает, что пора обновиться."""
        from apps.api.manifest import dataset_version

        payload = {
            'version': dataset_version(),
            'generated_at': timezone.now().isoformat(),
            'counts': {'heroes': len(heroes)},
            'heroes': [
                {
                    'id': hero.slug,
                    'name': hero.full_name,
                    'dates': hero.rank_dates,
                    'period': hero.period,
                    'branch': hero.branch.name if hero.branch else '',
                    'district': hero.birth_raion or None,
                    'biography': hero.biography_paragraphs,
                    'photos': [p for p in (self._existing_photo(ph) for ph in hero.photos.all()) if p],
                    'detail': '2022/detail/detail_%s.html' % hero.slug,
                }
                for hero in heroes
            ],
        }
        (self.out / 'data.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding='utf-8',
        )

        files = []
        for path in self.out.rglob('*'):
            if path.is_file():
                files.append({
                    'path': path.relative_to(self.out).as_posix(),
                    'size': path.stat().st_size,
                })

        sync = {
            'version': payload['version'],
            'generated_at': datetime.now().isoformat(timespec='seconds'),
            'files': len(files),
        }
        (self.out / 'sync.json').write_text(
            json.dumps(sync, ensure_ascii=False, indent=1), encoding='utf-8',
        )
        self.stats['files'] = len(files)
