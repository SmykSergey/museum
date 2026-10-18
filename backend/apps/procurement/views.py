"""Представления раздела «Державні закупівлі»."""

from django.db.models import Q
from django.views.generic import ListView

from .models import ProcurementDocument


class ProcurementListView(ListView):
    """Документы закупок с фильтром по году и поиском."""

    model = ProcurementDocument
    template_name = 'procurement/procurement_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = ProcurementDocument.objects.filter(is_published=True)

        year = (self.request.GET.get('year') or '').strip()
        if year.isdigit():
            queryset = queryset.filter(date__year=int(year))

        query = (self.request.GET.get('q') or '').strip()
        if query:
            queryset = queryset.filter(title__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        published = ProcurementDocument.objects.filter(is_published=True)
        years = (
            published
            .values_list('date__year', flat=True)
            .order_by('-date__year')
            .distinct()
        )

        context['years'] = list(years)
        context['active_year'] = (self.request.GET.get('year') or '').strip()
        context['query'] = (self.request.GET.get('q') or '').strip()
        context['total'] = published.count()
        return context
