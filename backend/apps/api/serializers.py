"""Сериализация данных для API.

Отдаём обычные словари — без DRF, чтобы не тащить лишнюю зависимость.
Все URL абсолютные: киоск обращается к API по сети и должен получить
ссылки, которые он сможет скачать сам.
"""

from django.templatetags.static import static

from apps.heroes.constants import district_map_slug


def _absolute(request, url):
    if not url:
        return None
    if request is None:
        return url
    return request.build_absolute_uri(url)


def hero_brief(hero, request=None):
    """Короткая карточка героя — то, что нужно для списка и карты."""
    district = (hero.birth_raion or '').strip()
    photo = hero.main_photo

    return {
        'id': hero.slug,
        'name': hero.full_name,
        'dates': hero.rank_dates,
        'period': hero.period,
        'branch': hero.branch.name if hero.branch else '',
        'branch_id': hero.branch_id,
        'district': district or None,
        'district_map': district_map_slug(district),
        'photo': _absolute(request, photo.image.url) if photo else None,
        'detail_url': _absolute(request, hero.get_absolute_url()),
        'updated_at': hero.updated_at.isoformat(),
    }


def hero_full(hero, request=None):
    """Полная карточка: биография, галерея, карта района."""
    data = hero_brief(hero, request)

    photos = list(hero.photos.all())
    data['biography'] = hero.biography_paragraphs
    data['photos'] = [
        {
            'url': _absolute(request, photo.image.url),
            'path': photo.image.name,
            'order': photo.order,
        }
        for photo in photos
    ]

    map_slug = data['district_map']
    data['map'] = _absolute(request, static('maps/%s.svg' % map_slug)) if map_slug else None

    return data


def branch_row(branch, request=None):
    return {
        'id': branch.pk,
        'name': branch.name,
        'order': branch.order,
        'heroes_count': getattr(branch, 'heroes_count', branch.heroes.count()),
    }


def district_row(name, count, request=None):
    map_slug = district_map_slug(name)
    return {
        'name': name,
        'heroes_count': count,
        'map_slug': map_slug,
        'map': _absolute(request, static('maps/%s.svg' % map_slug)) if map_slug else None,
    }
