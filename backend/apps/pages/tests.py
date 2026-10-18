"""Тесты страниц «Про музей» и «Історія музею»."""

from django.test import TestCase
from django.urls import reverse

from apps.exhibits.models import Exhibit
from apps.locations.models import Location

from .models import AboutPage, HistoryPage


class SingletonTests(TestCase):
    def test_about_page_is_single(self):
        first = AboutPage.load()
        second = AboutPage.load()

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(AboutPage.objects.count(), 1)

    def test_history_page_is_single(self):
        HistoryPage.load()
        HistoryPage.load()

        self.assertEqual(HistoryPage.objects.count(), 1)

    def test_saving_second_object_overwrites_first(self):
        AboutPage.load().save()
        page = AboutPage(title='Друга')
        page.save()

        self.assertEqual(AboutPage.objects.count(), 1)
        self.assertEqual(AboutPage.objects.first().title, 'Друга')


class PagesViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.location = Location.objects.create(
            name='Головний музей',
            address='вул. Гаванна, 4',
            schedule='Пн–Пт: 10:00 – 18:00',
            prices='<p>Квиток — 100 ₴</p>',
        )
        page = AboutPage.load()
        page.subtitle = 'Одеський історико-краєзнавчий музей'
        page.main_location = cls.location
        page.save()

        history = HistoryPage.load()
        history.title = 'Історія музею'
        history.body = '<p>Музей засновано давно.</p>'
        history.save()

        Exhibit.objects.create(
            title='Шолом', summary='Короткий опис', order=10,
        )

    def test_about_page(self):
        response = self.client.get(reverse('pages:about'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Про музей')
        self.assertContains(response, 'Одеський історико-краєзнавчий музей')
        # данные локации подтягиваются на страницу
        self.assertContains(response, 'вул. Гаванна, 4')
        self.assertContains(response, 'Квиток — 100 ₴')

    def test_about_page_shows_exhibits(self):
        response = self.client.get(reverse('pages:about'))

        self.assertContains(response, 'Шолом')
        self.assertEqual(len(response.context['exhibits']), 1)

    def test_about_page_hides_unpublished_exhibits(self):
        Exhibit.objects.create(title='Схований', is_published=False)

        response = self.client.get(reverse('pages:about'))

        self.assertNotContains(response, 'Схований')

    def test_history_page(self):
        response = self.client.get(reverse('pages:history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Історія музею')
        self.assertContains(response, 'Музей засновано давно.')
