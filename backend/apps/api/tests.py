"""Тесты read-only API для киоска."""

import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.heroes.models import Branch, Hero, HeroPhoto


class ApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.zsu = Branch.objects.create(name='Збройні Сили України', order=10)
        cls.dpsu = Branch.objects.create(name='Державна прикордонна служба України', order=20)

        cls.hero_a = Hero.objects.create(
            full_name='Андрієнко Петро Іванович',
            rank_dates='(01.01.1980 – 02.02.2023)',
            period='2022',
            branch=cls.zsu,
            birth_raion='Одеський',
            biography='Перший абзац.\nДругий абзац.',
        )
        cls.hero_b = Hero.objects.create(
            full_name='Бондаренко Іван Сергійович',
            period='2022',
            branch=cls.dpsu,
            birth_raion='Ізмаїльський',
        )
        cls.hero_old = Hero.objects.create(
            full_name='Агапій Олександр Петрович',
            period='2014',
            branch=cls.zsu,
            birth_raion='Одеський',
        )
        cls.hidden = Hero.objects.create(
            full_name='Схований Герой', period='2022', is_published=False,
        )

        HeroPhoto.objects.create(hero=cls.hero_a, image='heroes/x/1.jpg', order=0)
        HeroPhoto.objects.create(hero=cls.hero_a, image='heroes/x/2.jpg', order=1)


class PingTests(ApiTestCase):
    def test_ping(self):
        response = self.client.get('/api/v1/ping/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['counts']['heroes'], 3)  # скрытый не считаем
        self.assertEqual(data['counts']['photos'], 2)
        self.assertEqual(data['counts']['branches'], 2)
        self.assertTrue(data['version'])


class BranchTests(ApiTestCase):
    def test_branches(self):
        response = self.client.get('/api/v1/branches/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        names = [row['name'] for row in data['results']]
        self.assertEqual(names[0], 'Збройні Сили України')

    def test_branch_heroes_count(self):
        response = self.client.get('/api/v1/branches/')

        rows = {row['name']: row['heroes_count'] for row in response.json()['results']}
        self.assertEqual(rows['Збройні Сили України'], 2)


class DistrictTests(ApiTestCase):
    def test_districts(self):
        response = self.client.get('/api/v1/districts/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['without_district'], 0)

    def test_district_counts_are_grouped(self):
        # регрессия: Meta.ordering модели ломал GROUP BY и все счётчики были равны 1
        response = self.client.get('/api/v1/districts/')

        rows = {row['name']: row['heroes_count'] for row in response.json()['results']}
        self.assertEqual(rows['Одеський'], 2)
        self.assertEqual(rows['Ізмаїльський'], 1)

    def test_district_has_map(self):
        response = self.client.get('/api/v1/districts/')

        rows = {row['name']: row for row in response.json()['results']}
        self.assertEqual(rows['Одеський']['map_slug'], 'odesa')
        self.assertTrue(rows['Одеський']['map'].endswith('/static/maps/odesa.svg'))


class HeroListTests(ApiTestCase):
    def test_list_hides_unpublished(self):
        response = self.client.get('/api/v1/heroes/')

        names = [row['name'] for row in response.json()['results']]
        self.assertIn('Андрієнко Петро Іванович', names)
        self.assertNotIn('Схований Герой', names)

    def test_list_ordered_by_ukrainian_alphabet(self):
        response = self.client.get('/api/v1/heroes/')

        names = [row['name'] for row in response.json()['results']]
        self.assertLess(names.index('Агапій Олександр Петрович'),
                        names.index('Бондаренко Іван Сергійович'))

    def test_filter_by_period(self):
        response = self.client.get('/api/v1/heroes/', {'period': '2014'})

        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'Агапій Олександр Петрович')

    def test_filter_by_branch(self):
        response = self.client.get('/api/v1/heroes/', {'branch': self.dpsu.pk})

        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'Бондаренко Іван Сергійович')

    def test_filter_by_district(self):
        response = self.client.get('/api/v1/heroes/', {'district': 'Одеський'})

        self.assertEqual(response.json()['count'], 2)

    def test_search_by_name(self):
        response = self.client.get('/api/v1/heroes/', {'q': 'бондар'})

        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'Бондаренко Іван Сергійович')

    def test_pagination(self):
        response = self.client.get('/api/v1/heroes/', {'limit': 1, 'offset': 1})

        data = response.json()
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['results']), 1)

    def test_brief_card_fields(self):
        response = self.client.get('/api/v1/heroes/', {'q': 'Андрієнко'})

        row = response.json()['results'][0]
        self.assertEqual(row['id'], self.hero_a.slug)
        self.assertEqual(row['dates'], '(01.01.1980 – 02.02.2023)')
        self.assertEqual(row['branch'], 'Збройні Сили України')
        self.assertEqual(row['district'], 'Одеський')
        self.assertEqual(row['district_map'], 'odesa')
        self.assertTrue(row['photo'].endswith('/media/heroes/x/1.jpg'))
        self.assertTrue(row['detail_url'].endswith(self.hero_a.get_absolute_url()))


class HeroDetailTests(ApiTestCase):
    def test_detail(self):
        response = self.client.get('/api/v1/heroes/%s/' % self.hero_a.slug)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Андрієнко Петро Іванович')
        self.assertEqual(data['biography'], ['Перший абзац.', 'Другий абзац.'])
        self.assertEqual(len(data['photos']), 2)
        self.assertTrue(data['map'].endswith('/static/maps/odesa.svg'))

    def test_detail_unknown_returns_404(self):
        response = self.client.get('/api/v1/heroes/nesnuyuchyi/')

        self.assertEqual(response.status_code, 404)

    def test_detail_hides_unpublished(self):
        response = self.client.get('/api/v1/heroes/%s/' % self.hidden.slug)

        self.assertEqual(response.status_code, 404)


class SyncTests(ApiTestCase):
    def test_sync_payload(self):
        response = self.client.get('/api/v1/sync/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['counts']['heroes'], 3)
        self.assertEqual(len(data['heroes']), 3)
        self.assertEqual(data['branches'][0]['name'], 'Збройні Сили України')
        self.assertTrue(data['version'])
        self.assertIsInstance(data['files'], list)

    def test_sync_returns_304_with_etag(self):
        first = self.client.get('/api/v1/sync/')

        response = self.client.get('/api/v1/sync/', HTTP_IF_NONE_MATCH=first['ETag'])

        self.assertEqual(response.status_code, 304)

    def test_sync_not_modified_when_since_matches(self):
        version = self.client.get('/api/v1/sync/').json()['version']

        response = self.client.get('/api/v1/sync/', {'since': version})

        self.assertTrue(response.json()['not_modified'])

    def test_sync_version_changes_when_data_changes(self):
        version = self.client.get('/api/v1/sync/').json()['version']

        Hero.objects.create(full_name='Новий Герой', period='2022')

        new_version = self.client.get('/api/v1/sync/').json()['version']
        self.assertNotEqual(version, new_version)

    def test_sync_hero_has_biography_and_photos(self):
        data = self.client.get('/api/v1/sync/').json()

        hero = next(h for h in data['heroes'] if h['id'] == self.hero_a.slug)
        self.assertEqual(len(hero['biography']), 2)
        self.assertEqual(len(hero['photos']), 2)


class MethodTests(ApiTestCase):
    def test_only_get_allowed(self):
        response = self.client.post('/api/v1/heroes/')

        self.assertEqual(response.status_code, 405)
