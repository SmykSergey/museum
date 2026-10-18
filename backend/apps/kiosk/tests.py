"""Тесты сборки офлайн-бандла для киоска."""

import json
import tempfile
from pathlib import Path

from django.test import TestCase
from PIL import Image

from apps.heroes.models import Branch, Hero, HeroPhoto

from .builder import KioskBuilder, branch_code


def make_image(path, color='red'):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new('RGB', (20, 20), color).save(path, format='JPEG')


class KioskBuilderTests(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.media = self.tmp / 'media'
        self.media.mkdir()
        self.design = self.tmp / 'design'
        self.design.mkdir()
        self.out = self.tmp / 'kiosk'

        # минимальный «каркас» киоска вместо настоящего макета
        for name in ('index.html', 'portal.html', 'start_2022.html', 'style.css'):
            (self.design / name).write_text('<html><body>ok</body></html>', encoding='utf-8')

        self.override = self.settings(
            MEDIA_ROOT=str(self.media),
            KIOSK_DESIGN_DIR=str(self.design),
        )
        self.override.enable()
        self.addCleanup(self.override.disable)

        self.branch = Branch.objects.create(name='Збройні Сили України', order=10)
        self.hero = Hero.objects.create(
            full_name='Андрієнко Петро Іванович',
            rank_dates='(01.01.1980 – 02.02.2023)',
            branch=self.branch,
            birth_raion='Одеський',
            biography='Перший абзац.\nДругий абзац.',
        )
        photo_path = self.media / 'heroes' / self.hero.slug / '1.jpg'
        make_image(photo_path)
        HeroPhoto.objects.create(
            hero=self.hero, image='heroes/%s/1.jpg' % self.hero.slug, order=0,
        )

    def build(self, **kwargs):
        builder = KioskBuilder(out_dir=self.out, with_legacy=False, **kwargs)
        return builder.build()

    def test_builds_hero_detail_page(self):
        self.build()

        page = self.out / '2022' / 'detail' / ('detail_%s.html' % self.hero.slug)
        self.assertTrue(page.exists())
        html = page.read_text(encoding='utf-8')
        self.assertIn('Андрієнко Петро Іванович', html)
        self.assertIn('Перший абзац.', html)
        self.assertIn('maps/odesa.svg', html)  # карта района в галерее

    def test_copies_photos(self):
        self.build()

        photo = self.out / '2022' / 'Збройні Сили України' / self.hero.slug / '1.jpg'
        self.assertTrue(photo.exists())
        self.assertGreater(photo.stat().st_size, 0)

    def test_writes_soldiers_data(self):
        self.build()

        content = (self.out / 'soldiers_data.js').read_text(encoding='utf-8')
        self.assertIn('const SOLDIERS_DATA', content)
        self.assertIn(self.hero.slug, content)
        self.assertIn('Одеський', content)

    def test_writes_preview_page_per_branch(self):
        self.build()

        self.assertTrue((self.out / 'preview_zsu.html').exists())

    def test_writes_data_json(self):
        self.build()

        data = json.loads((self.out / 'data.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['heroes']), 1)
        self.assertEqual(data['heroes'][0]['id'], self.hero.slug)
        self.assertTrue(data['version'])

    def test_writes_sync_json(self):
        self.build()

        sync = json.loads((self.out / 'sync.json').read_text(encoding='utf-8'))
        self.assertTrue(sync['version'])
        self.assertGreater(sync['files'], 0)

    def test_no_broken_local_links(self):
        stats = self.build()

        self.assertEqual(stats['broken_links'], 0, stats.get('missing_links'))

    def test_hides_unpublished_heroes(self):
        Hero.objects.create(full_name='Схований Герой', is_published=False)

        self.build()

        data = json.loads((self.out / 'data.json').read_text(encoding='utf-8'))
        names = [hero['name'] for hero in data['heroes']]
        self.assertNotIn('Схований Герой', names)

    def test_skips_broken_photo_without_failing(self):
        # пустой файл в media не должен ронять сборку
        broken = self.media / 'heroes' / 'broken' / '1.jpg'
        broken.parent.mkdir(parents=True, exist_ok=True)
        broken.write_bytes(b'')

        hero = Hero.objects.create(full_name='Без Фото', branch=self.branch)
        HeroPhoto.objects.create(hero=hero, image='heroes/broken/1.jpg', order=0)

        stats = self.build()

        self.assertEqual(stats['broken'], 1)
        self.assertEqual(stats['broken_links'], 0)


class BranchCodeTests(TestCase):
    def test_known_branches(self):
        self.assertEqual(branch_code('Збройні Сили України'), 'zsu')
        self.assertEqual(branch_code('Державна прикордонна служба України'), 'dpsu')
        self.assertEqual(branch_code('Служба безпеки України'), 'sbu')

    def test_unknown_branch_gets_slug(self):
        self.assertEqual(branch_code('Невідомий підрозділ'), 'nevidomyi-pidrozdil')
