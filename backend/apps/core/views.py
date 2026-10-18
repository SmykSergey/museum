from django.shortcuts import render

from apps.events.models import Event
from apps.locations.models import Location
from apps.news.models import NewsItem


def home(request):
    """Главная страница музея: локации, ближайшие события и последние новости."""
    published_locations = (
        Location.objects
        .filter(is_published=True)
        .order_by('order', 'name')
    )

    context = {
        'locations': published_locations,
        'events': Event.objects.upcoming()[:4],
        'news': NewsItem.objects.recent()[:4],
        # в блоке «Контакти» показываются те же площадки, но с графиком и адресом
        'contacts': published_locations,
    }
    return render(request, 'core/home.html', context)
