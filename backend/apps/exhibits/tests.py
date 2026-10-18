"""Тесты экспонатов."""

from django.test import TestCase

from .models import Exhibit


class ExhibitModelTests(TestCase):
    def test_slug_generated_from_title(self):
        exhibit = Exhibit.objects.create(title='Шолом типу «Моріон»')

        self.assertEqual(exhibit.slug, 'sholom-typu-morion')

    def test_slug_is_unique(self):
        Exhibit.objects.create(title='Шолом')
        second = Exhibit.objects.create(title='Шолом')

        self.assertEqual(second.slug, 'sholom-2')

    def test_ordering_by_order(self):
        second = Exhibit.objects.create(title='Другий', order=20)
        first = Exhibit.objects.create(title='Перший', order=10)

        self.assertEqual(list(Exhibit.objects.all()), [first, second])

    def test_str(self):
        exhibit = Exhibit.objects.create(title='Шолом')

        self.assertEqual(str(exhibit), 'Шолом')


class ExhibitViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.exhibit = Exhibit.objects.create(
            title='Шолом типу «Моріон»',
            summary='Зразок захисного озброєння',
            body='<p>Детальний опис експоната.</p>',
        )
        cls.hidden = Exhibit.objects.create(title='Схований', is_published=False)

    def test_detail_page(self):
        response = self.client.get(self.exhibit.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Шолом типу «Моріон»')
        self.assertContains(response, 'Детальний опис експоната.')

    def test_detail_hides_unpublished(self):
        response = self.client.get(self.hidden.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_unknown_exhibit_returns_404(self):
        response = self.client.get('/exhibits/nesnuyuchyi/')

        self.assertEqual(response.status_code, 404)
