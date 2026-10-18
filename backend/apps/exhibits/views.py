"""Представления экспонатов."""

from django.views.generic import DetailView

from .models import Exhibit


class ExhibitDetailView(DetailView):
    """Страница экспоната."""

    model = Exhibit
    template_name = 'exhibits/exhibit_detail.html'
    context_object_name = 'exhibit'

    def get_queryset(self):
        return Exhibit.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_exhibits'] = (
            Exhibit.objects.filter(is_published=True).exclude(pk=self.object.pk)[:3]
        )
        return context
