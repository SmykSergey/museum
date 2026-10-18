"""Тесты модели локаций."""

from django.test import TestCase
from django.urls import reverse

from .models import Location


class LocationModelTests(TestCase):
    def test_slug_generated_from_name(self):
        location = Location.objects.create(name='Музей Степова Україна')

        self.assertEqual(location.slug, 'muzei-stepova-ukraina')

    def test_slug_is_unique(self):
        Location.objects.create(name='Музей Степова Україна')
        second = Location.objects.create(name='Музей Степова Україна')

        self.assertEqual(second.slug, 'muzei-stepova-ukraina-2')

    def test_manual_slug_is_kept(self):
        location = Location.objects.create(name='Музей', slug='my-slug')

        self.assertEqual(location.slug, 'my-slug')

    def test_schedule_lines(self):
        location = Location.objects.create(
            name='Музей',
            schedule='Пн–Пт: 10:00 – 18:00\n\nСб: 10:00 – 17:00\n',
        )

        self.assertEqual(
            location.schedule_lines,
            ['Пн–Пт: 10:00 – 18:00', 'Сб: 10:00 – 17:00'],
        )

    def test_ordering_by_order_field(self):
        third = Location.objects.create(name='Третя', order=30)
        first = Location.objects.create(name='Перша', order=10)

        self.assertEqual(list(Location.objects.all()), [first, third])

    def test_str(self):
        location = Location.objects.create(name='Музей Степова Україна')

        self.assertEqual(str(location), 'Музей Степова Україна')


class LocationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from datetime import timedelta

        from django.utils import timezone

        from apps.events.models import Event

        cls.location = Location.objects.create(
            name='Головний музей', address='вул. Гаванна, 4',
            schedule='Пн–Пт: 10:00 – 18:00',
        )
        cls.hidden = Location.objects.create(name='Прихована', is_published=False)
        cls.event = Event.objects.create(
            title='Екскурсія', starts_at=timezone.now() + timedelta(days=2),
            location=cls.location,
        )

    def test_list_page(self):
        response = self.client.get(reverse('locations:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Головний музей')
        self.assertNotContains(response, 'Прихована')

    def test_detail_page(self):
        response = self.client.get(self.location.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'вул. Гаванна, 4')
        self.assertContains(response, 'Пн–Пт: 10:00 – 18:00')
        self.assertContains(response, 'Екскурсія')

    def test_detail_hides_unpublished(self):
        response = self.client.get(self.hidden.get_absolute_url())

        self.assertEqual(response.status_code, 404)
