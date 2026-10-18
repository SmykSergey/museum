"""Представления раздела «Герої не вмирають»."""

from django.shortcuts import get_object_or_404, render

from .models import Hero


def published_heroes():
    """Опубликованные герои с уже подгруженными связями, в украинском порядке."""
    return (
        Hero.objects
        .filter(is_published=True)
        .select_related('branch')
        .prefetch_related('photos')
    )


def group_by_letter(heroes):
    """Группирует отсортированный список героев по первой букве фамилии.

    Возвращает список словарей: [{'letter': 'А', 'heroes': [...]}, ...]
    """
    groups = []
    for hero in heroes:
        letter = hero.first_letter
        if not groups or groups[-1]['letter'] != letter:
            groups.append({'letter': letter, 'heroes': []})
        groups[-1]['heroes'].append(hero)
    return groups


def hero_list(request):
    """Список всех героев с поиском по фамилии и алфавитным указателем."""
    query = (request.GET.get('q') or '').strip()

    heroes = list(published_heroes())

    if query:
        needle = query.casefold()
        heroes = [h for h in heroes if needle in (h.full_name or '').casefold()]

    groups = group_by_letter(heroes)

    context = {
        'groups': groups,
        # буквы для алфавитной линейки: только те, что реально есть в выборке
        'letters': [group['letter'] for group in groups],
        'query': query,
        'found_count': len(heroes),
        'total_count': Hero.objects.filter(is_published=True).count(),
    }
    return render(request, 'heroes/hero_list.html', context)


def hero_detail(request, slug):
    """Страница героя с галереей и переходом к соседним записям."""
    hero = get_object_or_404(published_heroes(), slug=slug)

    # Соседи считаются по полному отсортированному списку: навигация
    # замыкается по кругу, как в исходной вёрстке.
    slugs = list(
        Hero.objects.filter(is_published=True)
        .order_by('sort_key', 'full_name')
        .values_list('slug', flat=True)
    )
    prev_hero = next_hero = None
    if len(slugs) > 1 and slug in slugs:
        index = slugs.index(slug)
        prev_hero = Hero.objects.filter(slug=slugs[index - 1]).first()
        next_hero = Hero.objects.filter(slug=slugs[(index + 1) % len(slugs)]).first()

    context = {
        'hero': hero,
        'paragraphs': hero.biography_paragraphs,
        'gallery': hero.gallery,
        'prev_hero': prev_hero,
        'next_hero': next_hero,
    }
    return render(request, 'heroes/hero_detail.html', context)
