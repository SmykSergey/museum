"""Тесты раздела «Державні закупівлі»."""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import ProcurementDocument


class ProcurementDocumentTests(TestCase):
    def test_year_property(self):
        doc = ProcurementDocument.objects.create(
            date=date(2025, 3, 14), title='Зміни до плану',
        )

        self.assertEqual(doc.year, 2025)

    def test_download_url_empty(self):
        doc = ProcurementDocument.objects.create(
            date=date(2025, 3, 14), title='Документ',
        )

        self.assertEqual(doc.download_url, '')

    def test_ordering_newest_first(self):
        old = ProcurementDocument.objects.create(date=date(2024, 1, 1), title='Старий')
        new = ProcurementDocument.objects.create(date=date(2026, 1, 1), title='Новий')

        self.assertEqual(list(ProcurementDocument.objects.all()), [new, old])


class ProcurementViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc_2026 = ProcurementDocument.objects.create(
            date=date(2026, 1, 21), title='Річний план на 2026 рік',
        )
        cls.doc_2025 = ProcurementDocument.objects.create(
            date=date(2025, 3, 10), title='Обґрунтування закупівлі теплопостачання',
        )
        cls.hidden = ProcurementDocument.objects.create(
            date=date(2025, 5, 5), title='Чернетка', is_published=False,
        )

    def test_list_page(self):
        response = self.client.get(reverse('procurement:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Річний план на 2026 рік')
        self.assertNotContains(response, 'Чернетка')

    def test_documents_grouped_by_year(self):
        response = self.client.get(reverse('procurement:list'))

        years = sorted({doc.year for doc in response.context['documents']}, reverse=True)
        self.assertEqual(years, [2026, 2025])

    def test_years_in_context(self):
        response = self.client.get(reverse('procurement:list'))

        self.assertEqual(response.context['years'], [2026, 2025])

    def test_filter_by_year(self):
        response = self.client.get(reverse('procurement:list'), {'year': '2025'})

        self.assertEqual(len(response.context['documents']), 1)
        self.assertEqual(response.context['documents'][0].year, 2025)

    def test_search_by_title(self):
        response = self.client.get(reverse('procurement:list'), {'q': 'тепло'})

        self.assertEqual(len(response.context['documents']), 1)
        self.assertContains(response, 'теплопостачання')

    def test_search_without_results(self):
        response = self.client.get(reverse('procurement:list'), {'q': 'неіснуючий'})

        self.assertEqual(len(response.context['documents']), 0)
        self.assertContains(response, 'не знайдено')

    def test_total_counts_only_published(self):
        response = self.client.get(reverse('procurement:list'))

        self.assertEqual(response.context['total'], 2)
