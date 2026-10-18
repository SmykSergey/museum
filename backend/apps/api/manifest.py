"""Манифест файлов и версия набора данных.

Киоск скачивает файлы только если их контрольная сумма изменилась,
поэтому манифест с sha256 — ключевая часть синхронизации.

Посчитать sha256 для 1003 фото (178 МБ) на каждый запрос слишком дорого,
поэтому результат кэшируется в media/.manifest_cache.json: если размер
и время изменения файла не поменялись — берём готовый хеш.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db.models import Max
from django.templatetags.static import static

from apps.heroes.constants import DISTRICT_MAPS
from apps.heroes.models import Branch, Hero, HeroPhoto

CACHE_FILENAME = '.manifest_cache.json'


def _cache_path():
    return Path(settings.MEDIA_ROOT) / CACHE_FILENAME


def _load_cache():
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache):
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(cache), encoding='utf-8')
    tmp.replace(path)


def file_sha256(path, cache):
    """sha256 файла с кэшем по (размер, mtime)."""
    stat = path.stat()
    key = path.as_posix()
    entry = cache.get(key)

    if entry and entry.get('size') == stat.st_size and entry.get('mtime') == stat.st_mtime:
        return entry['sha256']

    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)

    value = digest.hexdigest()
    cache[key] = {'size': stat.st_size, 'mtime': stat.st_mtime, 'sha256': value}
    return value


def dataset_version():
    """Короткая версия состояния данных.

    Меняется, когда добавили/удалили героя, фото или ветку. Киоск сравнивает
    её со своей и не делает лишних запросов, если ничего не поменялось.
    """
    last_hero = Hero.objects.aggregate(last=Max('updated_at'))['last']
    last_photo = HeroPhoto.objects.aggregate(last=Max('id'))['last']

    raw = '|'.join([
        str(Hero.objects.count()),
        str(HeroPhoto.objects.count()),
        str(Branch.objects.count()),
        last_hero.isoformat() if last_hero else '',
        str(last_photo),
    ])
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]


def photo_files():
    """Файлы фотографий, на которые ссылается база."""
    media_root = Path(settings.MEDIA_ROOT)
    for photo in HeroPhoto.objects.all().only('image'):
        path = media_root / photo.image.name
        if path.exists():
            yield photo.image.name, path


def district_map_files():
    """SVG-карты районов из static/maps."""
    static_root = Path(settings.BASE_DIR) / 'static' / 'maps'
    for slug in DISTRICT_MAPS.values():
        path = static_root / ('%s.svg' % slug)
        if path.exists():
            yield 'maps/%s.svg' % slug, path


def build_file_manifest(request=None):
    """Манифест всех файлов, которые нужны киоску: фото + карты районов."""
    cache = _load_cache()
    media_root = Path(settings.MEDIA_ROOT)
    files = []

    for relative, path in photo_files():
        item = {
            'path': relative,
            'size': path.stat().st_size,
            'sha256': file_sha256(path, cache),
            'kind': 'photo',
        }
        if request is not None:
            item['url'] = request.build_absolute_uri(settings.MEDIA_URL + relative)
        files.append(item)

    for relative, path in district_map_files():
        item = {
            'path': relative,
            'size': path.stat().st_size,
            'sha256': file_sha256(path, cache),
            'kind': 'map',
        }
        if request is not None:
            item['url'] = request.build_absolute_uri(static(relative))
        files.append(item)

    _save_cache(cache)
    return files
