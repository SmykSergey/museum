"""Представления локаций."""

from django.views.generic import DetailView, ListView

from apps.events.models import Event

from .models import Location


class LocationListView(ListView):
    """Все площадки музея."""

    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 12

    def get_queryset(self):
        return Location.objects.filter(is_published=True).order_by('order', 'name')


class LocationDetailView(DetailView):
    """Страница локации: адрес, график, цены, описание и события площадки."""

    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'

    def get_queryset(self):
        return Location.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = Event.objects.upcoming().filter(location=self.object)[:4]
        context['other_locations'] = (
            Location.objects.filter(is_published=True).exclude(pk=self.object.pk)[:3]
        )
        return context
