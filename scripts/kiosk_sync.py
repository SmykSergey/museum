#!/usr/bin/env python3
"""Синхронизация киоска с сайтом.

Запускается на машине, рядом с которой стоит сенсорный стол (или прямо на нём).
Скрипт использует только стандартную библиотеку Python 3.8+.

Что делает:
  1. спрашивает у сайта версию данных (/api/v1/ping/);
  2. сравнивает с версией в локальной папке киоска (sync.json);
  3. если версии разные — скачивает готовый архив (/api/v1/bundle/) и
     распаковывает его поверх локальной папки;
  4. старую версию сохраняет в резервную копию.

Запуск:
    python kiosk_sync.py
    python kiosk_sync.py --api http://127.0.0.1:8010 --dir D:/kiosk
    python kiosk_sync.py --check          # только проверить, есть ли обновление
    python kiosk_sync.py --force          # обновить, даже если версия совпадает

Вернуться к предыдущей версии:
    заменить папку киоска на содержимое D:/kiosk_backup/<версия>/
"""

import argparse
import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

DEFAULT_API = 'http://127.0.0.1:8010'
DEFAULT_DIR = Path(__file__).resolve().parent / 'kiosk'
TIMEOUT = 60
CHUNK = 1024 * 256


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode('utf-8'))


def download(url, target):
    """Скачивает файл с индикатором прогресса."""
    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        total = int(response.headers.get('Content-Length') or 0)
        done = 0
        target.parent.mkdir(parents=True, exist_ok=True)

        last_percent = -1
        with open(target, 'wb') as fh:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                fh.write(chunk)
                done += len(chunk)
                if total:
                    percent = done * 100 // total
                    if percent != last_percent:
                        last_percent = percent
                        print('\r  скачано %3d%% (%.1f из %.1f МБ)'
                              % (percent, done / 1048576, total / 1048576), end='')
        print()


def local_version(kiosk_dir):
    sync_file = kiosk_dir / 'sync.json'
    if not sync_file.exists():
        return None
    try:
        return json.loads(sync_file.read_text(encoding='utf-8')).get('version')
    except (OSError, json.JSONDecodeError):
        return None


def backup(kiosk_dir, version):
    if not kiosk_dir.exists():
        return None

    stamp = version or datetime.now().strftime('%Y%m%d-%H%M%S')
    target = kiosk_dir.parent / ('%s_backup' % kiosk_dir.name) / stamp
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(kiosk_dir, target)
    return target


def extract(archive, kiosk_dir):
    """Распаковывает архив поверх папки киоска."""
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(kiosk_dir)


def main():
    parser = argparse.ArgumentParser(description='Обновление киоска с сайта музея')
    parser.add_argument('--api', default=DEFAULT_API, help='Адрес сайта')
    parser.add_argument('--dir', default=str(DEFAULT_DIR), help='Папка киоска на столе')
    parser.add_argument('--check', action='store_true', help='Только проверить версию')
    parser.add_argument('--force', action='store_true', help='Обновить принудительно')
    parser.add_argument('--keep-backup', action='store_true', default=True,
                        help='Сохранять резервную копию (по умолчанию да)')
    args = parser.parse_args()

    api = args.api.rstrip('/')
    kiosk_dir = Path(args.dir)

    print('Сайт:  %s' % api)
    print('Киоск: %s' % kiosk_dir)
    print()

    try:
        ping = fetch_json(api + '/api/v1/ping/')
    except Exception as error:  # noqa: BLE001 — сеть может быть недоступна
        print('НЕ УДАЛОСЬ СВЯЗАТЬСЯ С САЙТОМ: %s' % error)
        print('Проверьте интернет и адрес, например: --api http://museum.example.com')
        return 1

    server_version = ping.get('version')
    current = local_version(kiosk_dir)

    print('Версия на сайте: %s' % server_version)
    print('Версия в киоске: %s' % (current or 'нет данных'))
    print('Героев на сайте: %s' % ping.get('counts', {}).get('heroes', '?'))
    print()

    if current == server_version and not args.force:
        print('Обновление не требуется — данные совпадают.')
        return 0

    if args.check:
        print('Есть обновление. Запустите скрипт без --check, чтобы скачать.')
        return 0

    if args.keep_backup and kiosk_dir.exists():
        saved = backup(kiosk_dir, current)
        if saved:
            print('Резервная копия: %s' % saved)
            print()

    archive = Path(tempfile.mkdtemp()) / 'kiosk.zip'
    print('Скачивание архива с сайта...')
    try:
        download(api + '/api/v1/bundle/', archive)
    except Exception as error:  # noqa: BLE001
        print('НЕ УДАЛОСЬ СКАЧАТЬ АРХИВ: %s' % error)
        print('Скорее всего, на сервере не собран бандл:')
        print('  python manage.py build_kiosk --zip')
        return 1

    print('Распаковка...')
    kiosk_dir.mkdir(parents=True, exist_ok=True)
    extract(archive, kiosk_dir)

    shutil.rmtree(archive.parent, ignore_errors=True)

    new_version = local_version(kiosk_dir)
    print()
    print('ГОТОВО. Версия киоска: %s' % new_version)
    print('Откройте на столе index.html (или перезагрузите страницу).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
