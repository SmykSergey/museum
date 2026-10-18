"""Представления библиотеки."""

from django.db.models import Q
from django.views.generic import ListView

from .models import LibraryIssue


class LibraryListView(ListView):
    """Список выпусков «Вісника» с поиском по названию и номеру."""

    model = LibraryIssue
    template_name = 'library/library_list.html'
    context_object_name = 'issues'
    paginate_by = 24

    def get_queryset(self):
        queryset = LibraryIssue.objects.filter(is_published=True)

        query = (self.request.GET.get('q') or '').strip()
        if query:
            # поиск и по названию, и по номеру выпуска
            condition = Q(title__icontains=query)
            if query.isdigit():
                condition |= Q(number=int(query))
            queryset = queryset.filter(condition)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = (self.request.GET.get('q') or '').strip()
        context['total'] = LibraryIssue.objects.filter(is_published=True).count()
        return context
