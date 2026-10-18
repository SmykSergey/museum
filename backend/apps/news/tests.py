"""Тесты модели новостей."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import NewsItem


class NewsItemModelTests(TestCase):
    def test_slug_generated_from_title(self):
        item = NewsItem.objects.create(title='Відкриття виставки')

        self.assertEqual(item.slug, 'vidkryttia-vystavky')

    def test_slug_is_unique(self):
        NewsItem.objects.create(title='Відкриття виставки')
        second = NewsItem.objects.create(title='Відкриття виставки')

        self.assertEqual(second.slug, 'vidkryttia-vystavky-2')

    def test_published_hides_unpublished(self):
        NewsItem.objects.create(title='Чернетка', is_published=False)
        published = NewsItem.objects.create(title='Опублікована')

        self.assertEqual(list(NewsItem.objects.published()), [published])

    def test_recent_sorts_newest_first(self):
        now = timezone.now()
        old = NewsItem.objects.create(title='Стара', published_at=now - timedelta(days=10))
        new = NewsItem.objects.create(title='Нова', published_at=now)

        self.assertEqual(list(NewsItem.objects.recent()), [new, old])

    def test_recent_excludes_unpublished(self):
        NewsItem.objects.create(title='Чернетка', is_published=False)

        self.assertEqual(NewsItem.objects.recent().count(), 0)

    def test_str(self):
        item = NewsItem.objects.create(title='Відкриття виставки')

        self.assertEqual(str(item), 'Відкриття виставки')


class NewsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        for i in range(7):
            NewsItem.objects.create(
                title='Новина %s' % i,
                summary='Опис %s' % i,
                published_at=now - timedelta(days=i),
            )
        cls.draft = NewsItem.objects.create(title='Чернетка', is_published=False)

    def test_list_page(self):
        response = self.client.get(reverse('news:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новина 0')
        self.assertNotContains(response, 'Чернетка')

    def test_list_is_paginated(self):
        response = self.client.get(reverse('news:list'))

        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['news_list']), 6)

    def test_second_page(self):
        response = self.client.get(reverse('news:list'), {'page': 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['news_list']), 1)

    def test_list_sorted_newest_first(self):
        response = self.client.get(reverse('news:list'))

        self.assertEqual(response.context['news_list'][0].title, 'Новина 0')

    def test_detail_page(self):
        item = NewsItem.objects.get(title='Новина 0')
        response = self.client.get(item.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новина 0')

    def test_detail_hides_unpublished(self):
        response = self.client.get(self.draft.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_unknown_news_returns_404(self):
        response = self.client.get('/news/nesnuyucha-novyna/')

        self.assertEqual(response.status_code, 404)
