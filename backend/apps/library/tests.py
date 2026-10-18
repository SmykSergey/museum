"""Тесты библиотеки."""

from django.test import TestCase
from django.urls import reverse

from .models import LibraryIssue


class LibraryIssueTests(TestCase):
    def test_display_title_default(self):
        issue = LibraryIssue.objects.create(number=1)

        self.assertEqual(issue.display_title, 'Вісник музею')

    def test_display_title_custom(self):
        issue = LibraryIssue.objects.create(number=1, title='Спецвипуск')

        self.assertEqual(issue.display_title, 'Спецвипуск')

    def test_download_url_from_file(self):
        issue = LibraryIssue.objects.create(number=1, file='library/visnyk-01.pdf')

        self.assertTrue(issue.download_url.endswith('visnyk-01.pdf'))

    def test_download_url_from_external_link(self):
        issue = LibraryIssue.objects.create(
            number=1, external_url='https://example.com/visnyk.pdf',
        )

        self.assertEqual(issue.download_url, 'https://example.com/visnyk.pdf')

    def test_download_url_empty(self):
        issue = LibraryIssue.objects.create(number=1)

        self.assertEqual(issue.download_url, '')

    def test_ordering_newest_first(self):
        first = LibraryIssue.objects.create(number=1)
        second = LibraryIssue.objects.create(number=2)

        self.assertEqual(list(LibraryIssue.objects.all()), [second, first])


class LibraryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for number in range(1, 23):
            LibraryIssue.objects.create(number=number, title='Вісник музею')
        cls.hidden = LibraryIssue.objects.create(number=99, is_published=False)

    def test_list_page(self):
        response = self.client.get(reverse('library:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '№22')
        self.assertNotContains(response, '№99')

    def test_search_by_number(self):
        response = self.client.get(reverse('library:list'), {'q': '5'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['issues']), 1)
        self.assertEqual(response.context['issues'][0].number, 5)

    def test_search_by_title(self):
        LibraryIssue.objects.create(number=50, title='Спецвипуск про Одесу')

        response = self.client.get(reverse('library:list'), {'q': 'спецвипуск'})

        self.assertEqual(len(response.context['issues']), 1)

    def test_search_without_results(self):
        response = self.client.get(reverse('library:list'), {'q': 'неіснуючий'})

        self.assertEqual(len(response.context['issues']), 0)
        self.assertContains(response, 'не знайдено')

    def test_list_is_paginated_when_many_issues(self):
        for number in range(100, 110):
            LibraryIssue.objects.create(number=number)

        response = self.client.get(reverse('library:list'))

        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['issues']), 24)
