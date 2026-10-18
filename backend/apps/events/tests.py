"""Тесты модели событий."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.locations.models import Location

from .models import Event


class EventModelTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name='Головний музей')

    def test_slug_generated_from_title(self):
        event = Event.objects.create(title='Лекція про степ', starts_at=timezone.now())

        self.assertEqual(event.slug, 'lektsiia-pro-step')

    def test_is_past(self):
        past = Event.objects.create(
            title='Минула', starts_at=timezone.now() - timedelta(days=1),
        )
        future = Event.objects.create(
            title='Майбутня', starts_at=timezone.now() + timedelta(days=1),
        )

        self.assertTrue(past.is_past)
        self.assertFalse(future.is_past)

    def test_upcoming_contains_only_future_events(self):
        future = Event.objects.create(
            title='Майбутня', starts_at=timezone.now() + timedelta(days=1),
        )
        Event.objects.create(title='Минула', starts_at=timezone.now() - timedelta(days=1))

        self.assertEqual(list(Event.objects.upcoming()), [future])

    def test_upcoming_excludes_manually_archived(self):
        Event.objects.create(
            title='Скасована', starts_at=timezone.now() + timedelta(days=1),
            is_archived=True,
        )

        self.assertEqual(Event.objects.upcoming().count(), 0)

    def test_archive_contains_past_and_manually_archived(self):
        past = Event.objects.create(
            title='Минула', starts_at=timezone.now() - timedelta(days=5),
        )
        cancelled = Event.objects.create(
            title='Скасована', starts_at=timezone.now() + timedelta(days=5),
            is_archived=True,
        )
        Event.objects.create(
            title='Майбутня', starts_at=timezone.now() + timedelta(days=5),
        )

        self.assertEqual(set(Event.objects.archive()), {past, cancelled})

    def test_archive_sorted_newest_first(self):
        older = Event.objects.create(
            title='Давня', starts_at=timezone.now() - timedelta(days=30),
        )
        recent = Event.objects.create(
            title='Недавня', starts_at=timezone.now() - timedelta(days=2),
        )

        self.assertEqual(list(Event.objects.archive()), [recent, older])

    def test_unpublished_event_is_nowhere(self):
        Event.objects.create(
            title='Чернетка', starts_at=timezone.now() + timedelta(days=1),
            is_published=False,
        )

        self.assertEqual(Event.objects.upcoming().count(), 0)
        self.assertEqual(Event.objects.archive().count(), 0)

    def test_location_link(self):
        event = Event.objects.create(
            title='Лекція', starts_at=timezone.now(), location=self.location,
        )

        self.assertEqual(event.location, self.location)
        self.assertEqual(list(self.location.events.all()), [event])

    def test_str(self):
        event = Event.objects.create(title='Лекція про степ', starts_at=timezone.now())

        self.assertEqual(str(event), 'Лекція про степ')


class EventViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.location = Location.objects.create(name='Головна площадка')
        cls.upcoming = Event.objects.create(
            title='Майбутня подія', summary='Опис',
            starts_at=now + timedelta(days=3), location=cls.location,
        )
        cls.past = Event.objects.create(
            title='Минула подія', starts_at=now - timedelta(days=3),
        )
        cls.draft = Event.objects.create(
            title='Чернетка', starts_at=now + timedelta(days=3), is_published=False,
        )

    def test_list_shows_only_upcoming(self):
        response = self.client.get(reverse('events:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Майбутня подія')
        self.assertNotContains(response, 'Минула подія')
        self.assertNotContains(response, 'Чернетка')

    def test_archive_shows_only_past(self):
        response = self.client.get(reverse('events:archive'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Минула подія')
        self.assertNotContains(response, 'Майбутня подія')

    def test_detail_page(self):
        response = self.client.get(self.upcoming.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Майбутня подія')
        self.assertContains(response, 'Головна площадка')

    def test_detail_hides_unpublished(self):
        response = self.client.get(self.draft.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_archive_url_is_not_treated_as_slug(self):
        # 'archive/' должен открывать архив, а не искать событие с таким slug
        response = self.client.get('/events/archive/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Архів подій')
