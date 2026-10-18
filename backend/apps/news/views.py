"""Представления новостей."""

from django.views.generic import DetailView, ListView

from .models import NewsItem


class NewsListView(ListView):
    """Список новостей: свежие первыми, с постраничной навигацией."""

    model = NewsItem
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 6

    def get_queryset(self):
        return NewsItem.objects.recent()


class NewsDetailView(DetailView):
    """Страница новости."""

    model = NewsItem
    template_name = 'news/news_detail.html'
    context_object_name = 'item'

    def get_queryset(self):
        # черновики по прямой ссылке тоже не показываем
        return NewsItem.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_news'] = NewsItem.objects.recent().exclude(pk=self.object.pk)[:3]
        return context
