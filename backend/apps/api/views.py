"""Read-only API для киоска.

Все эндпоинты только читают данные: киоск ничего не пишет на сайт, поэтому
никакой авторизации не нужно. Данные публичные — те же, что на сайте.
"""

from pathlib import Path

from django.conf import settings
from django.db.models import Count
from django.http import FileResponse, HttpResponseNotModified, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_safe

from apps.heroes.constants import DISTRICT_ORDER
from apps.heroes.models import Branch, Hero, HeroPhoto

from .manifest import build_file_manifest, dataset_version
from .serializers import branch_row, district_row, hero_brief, hero_full

# максимум записей за один запрос к списку
MAX_LIMIT = 1000
DEFAULT_LIMIT = 500


def json_response(payload, status=200, headers=None):
    response = JsonResponse(payload, status=status, json_dumps_params={'ensure_ascii': False})
    response['Cache-Control'] = 'public, max-age=60'
    for key, value in (headers or {}).items():
        response[key] = value
    return response


def published_heroes():
    return (
        Hero.objects
        .filter(is_published=True)
        .select_related('branch')
        .prefetch_related('photos')
    )


@require_safe
def ping(request):
    """Проверка связи и текущая версия данных."""
    return json_response({
        'status': 'ok',
        'version': dataset_version(),
        'server_time': timezone.now().isoformat(),
        'counts': {
            'heroes': Hero.objects.filter(is_published=True).count(),
            'photos': HeroPhoto.objects.filter(hero__is_published=True).count(),
            'branches': Branch.objects.count(),
        },
    })


@require_safe
def branches(request):
    """Список родов войск с количеством героев."""
    rows = Branch.objects.annotate(heroes_count=Count('heroes')).order_by('order', 'name')
    return json_response({
        'count': len(rows),
        'results': [branch_row(branch, request) for branch in rows],
    })


def district_rows(request):
    """Районы с количеством героев: сначала в порядке карты, потом остальные."""
    # order_by() обязателен: иначе Meta.ordering модели попадает в GROUP BY
    # и вместо группировки по району считаются отдельные герои
    counts = dict(
        Hero.objects
        .filter(is_published=True)
        .exclude(birth_raion='')
        .order_by()
        .values_list('birth_raion')
        .annotate(total=Count('id'))
    )

    ordered = [name for name in DISTRICT_ORDER if name in counts]
    ordered += [name for name in counts if name not in DISTRICT_ORDER]
    return [district_row(name, counts[name], request) for name in ordered]


@require_safe
def districts(request):
    """Список районов Одещины с количеством героев и ссылкой на карту."""
    results = district_rows(request)
    return json_response({
        'count': len(results),
        'without_district': Hero.objects.filter(
            is_published=True, birth_raion='',
        ).count(),
        'results': results,
    })


@require_safe
def hero_list(request):
    """Список героев с фильтрами: period, branch, district, q + limit/offset."""
    queryset = published_heroes()

    period = (request.GET.get('period') or '').strip()
    if period:
        queryset = queryset.filter(period=period)

    branch = (request.GET.get('branch') or '').strip()
    if branch.isdigit():
        queryset = queryset.filter(branch_id=int(branch))

    district = (request.GET.get('district') or '').strip()
    if district:
        queryset = queryset.filter(birth_raion=district)

    query = (request.GET.get('q') or '').strip()
    if query:
        queryset = queryset.filter(full_name__icontains=query)

    total = queryset.count()

    try:
        limit = int(request.GET.get('limit', DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    limit = max(1, min(limit, MAX_LIMIT))

    try:
        offset = max(0, int(request.GET.get('offset', 0)))
    except (TypeError, ValueError):
        offset = 0

    heroes = list(queryset[offset:offset + limit])

    return json_response({
        'count': total,
        'limit': limit,
        'offset': offset,
        'results': [hero_brief(hero, request) for hero in heroes],
    })


@require_safe
def hero_detail(request, slug):
    """Полная карточка героя: биография, галерея, карта района."""
    hero = get_object_or_404(published_heroes(), slug=slug)
    return json_response(hero_full(hero, request))


@require_safe
def sync(request):
    """Полный набор данных для киоска + манифест файлов.

    Киоск хранит у себя последнюю версию. Если `version` не изменилась,
    достаточно ответа `not_modified` и скачивать ничего не нужно.
    """
    version = dataset_version()
    etag = 'W/"%s"' % version

    if request.headers.get('If-None-Match') == etag:
        return HttpResponseNotModified()

    if (request.GET.get('since') or '').strip() == version:
        return json_response({'not_modified': True, 'version': version})

    heroes = list(published_heroes())
    branches_rows = Branch.objects.annotate(heroes_count=Count('heroes')).order_by('order', 'name')
    files = build_file_manifest(request)

    payload = {
        'version': version,
        'generated_at': timezone.now().isoformat(),
        'counts': {
            'heroes': len(heroes),
            'photos': sum(1 for h in heroes for _ in h.photos.all()),
            'branches': len(branches_rows),
            'files': len(files),
        },
        'branches': [branch_row(branch, request) for branch in branches_rows],
        'districts': district_rows(request),
        'heroes': [hero_full(hero, request) for hero in heroes],
        'files': files,
    }

    response = JsonResponse(
        payload, json_dumps_params={'ensure_ascii': False},
    )
    response['Cache-Control'] = 'no-cache'
    response['ETag'] = etag
    return response


@require_safe
def bundle(request):
    """Готовый архив киоска для синхронизации стола.

    Архив создаётся командой `python manage.py build_kiosk --zip`.
    Если файла нет — подсказываем, что делать.
    """
    import hashlib

    path = Path(settings.KIOSK_BUNDLE_PATH)
    if not path.exists():
        return json_response({
            'error': 'bundle_not_built',
            'detail': 'Архив киоска ещё не собран на сервере.',
            'how_to_fix': 'python manage.py build_kiosk --zip',
            'version': dataset_version(),
        }, status=404)

    stat = path.stat()
    etag = 'W/"%s-%s"' % (int(stat.st_mtime), stat.st_size)

    if request.headers.get('If-None-Match') == etag:
        return HttpResponseNotModified()

    response = FileResponse(
        path.open('rb'),
        as_attachment=True,
        filename='kiosk.zip',
        content_type='application/zip',
    )
    response['ETag'] = etag
    response['Content-Length'] = stat.st_size
    response['X-Kiosk-Version'] = dataset_version()
    return response
