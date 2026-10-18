"""Представления событий."""

from django.views.generic import DetailView, ListView

from .models import Event


class EventListView(ListView):
    """Актуальные события: ближайшие первыми."""

    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 6

    def get_queryset(self):
        return Event.objects.upcoming()


class EventArchiveView(ListView):
    """Архив: прошедшие события и то, что убрали в архив вручную."""

    model = Event
    template_name = 'events/event_archive.html'
    context_object_name = 'events'
    paginate_by = 6

    def get_queryset(self):
        return Event.objects.archive()


class EventDetailView(DetailView):
    """Страница события."""

    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.published().select_related('location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_events'] = Event.objects.upcoming().exclude(pk=self.object.pk)[:3]
        return context
