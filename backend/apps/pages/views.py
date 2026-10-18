"""Представления страниц «Про музей» и «Історія музею»."""

from django.shortcuts import render

from apps.exhibits.models import Exhibit

from .models import AboutPage, HistoryPage


def about(request):
    """Страница «Про музей»: карточки-разделы, экспозиция и контакты."""
    page = AboutPage.load()
    exhibits = Exhibit.objects.filter(is_published=True)

    context = {
        'page': page,
        'exhibits': exhibits,
        'location': page.main_location,
    }
    return render(request, 'pages/about.html', context)


def history(request):
    """Страница «Історія музею»."""
    page = HistoryPage.load()
    return render(request, 'pages/history.html', {'page': page})
