"""Тесты раздела «Герої не вмирають»."""

from django.test import TestCase
from django.urls import reverse

from apps.core.utils import make_sort_key, transliterate_uk

from .models import Branch, Hero, HeroPhoto


class SortKeyTests(TestCase):
    """Украинский алфавит: PostgreSQL сортирует кириллицу неверно, sort_key это чинит."""

    def test_order_of_ukrainian_letters(self):
        # И, І, Ї, Й должны идти именно в таком порядке
        self.assertLess(make_sort_key('Иваненко'), make_sort_key('Іваненко'))
        self.assertLess(make_sort_key('Іваненко'), make_sort_key('Їжакевич'))
        self.assertLess(make_sort_key('Їжакевич'), make_sort_key('Йосипенко'))

    def test_ge_and_ye_letters(self):
        self.assertLess(make_sort_key('Гаврилюк'), make_sort_key('Ґудзь'))
        self.assertLess(make_sort_key('Ґудзь'), make_sort_key('Данилюк'))

    def test_shorter_name_goes_first(self):
        self.assertLess(make_sort_key('Іванов'), make_sort_key('Іванова'))

    def test_empty_name(self):
        self.assertEqual(make_sort_key(''), '')


class TransliterationTests(TestCase):
    """Транслитерация нужна, чтобы адреса новых героев получались сами."""

    def test_surname_and_name(self):
        self.assertEqual(transliterate_uk('Шевченко Тарас'), 'Shevchenko Taras')

    def test_letters_that_depend_on_position(self):
        # Є, Ї, Й, Ю, Я в начале слова и в середине читаются по-разному
        self.assertEqual(transliterate_uk('Євген'), 'Yevhen')
        self.assertEqual(transliterate_uk('Андрієнко'), 'Andriienko')
        self.assertEqual(transliterate_uk('Їжакевич'), 'Yizhakevych')
        self.assertEqual(transliterate_uk('Юлія'), 'Yuliia')
        self.assertEqual(transliterate_uk('Ярошенко'), 'Yaroshenko')

    def test_apostrophe_is_dropped(self):
        self.assertEqual(transliterate_uk("В'ячеслав"), 'Viacheslav')

    def test_soft_sign_and_specific_letters(self):
        self.assertEqual(transliterate_uk('Хмельницький'), 'Khmelnytskyi')
        self.assertEqual(transliterate_uk('Ґудзь'), 'Gudz')


class HeroModelTests(TestCase):
    def setUp(self):
        self.hero = Hero.objects.create(
            full_name='Шевченко Тарас Григорович',
            slug='Shevchenko_Taras_Hryhorovych',
        )

    def test_sort_key_filled_on_save(self):
        self.assertTrue(self.hero.sort_key)

    def test_first_letter(self):
        self.assertEqual(self.hero.first_letter, 'Ш')

    def test_slug_generated_automatically(self):
        hero = Hero.objects.create(full_name='Коваленко Олена Петрівна')

        self.assertEqual(hero.slug, 'kovalenko-olena-petrivna')

    def test_slug_gets_suffix_when_taken(self):
        Hero.objects.create(full_name='Коваленко Олена Петрівна')
        second = Hero.objects.create(full_name='Коваленко Олена Петрівна')

        self.assertEqual(second.slug, 'kovalenko-olena-petrivna-2')

    def test_main_photo_is_first_by_order(self):
        HeroPhoto.objects.create(hero=self.hero, image='heroes/x/2.jpg', order=5)
        HeroPhoto.objects.create(hero=self.hero, image='heroes/x/1.jpg', order=1)

        self.assertTrue(self.hero.main_photo.image.name.endswith('1.jpg'))

    def test_gallery_excludes_main_photo(self):
        HeroPhoto.objects.create(hero=self.hero, image='heroes/x/1.jpg', order=0)
        HeroPhoto.objects.create(hero=self.hero, image='heroes/x/2.jpg', order=1)

        self.assertEqual(len(self.hero.gallery), 1)
        self.assertTrue(self.hero.gallery[0].image.name.endswith('2.jpg'))

    def test_biography_paragraphs_ignores_empty_lines(self):
        self.hero.biography = 'Первый абзац.\n\n\nВторой абзац.\n'
        self.hero.save()

        self.assertEqual(self.hero.biography_paragraphs, ['Первый абзац.', 'Второй абзац.'])

    def test_absolute_url(self):
        self.assertEqual(self.hero.get_absolute_url(), '/geroi/Shevchenko_Taras_Hryhorovych/')

    def test_str(self):
        self.assertEqual(str(self.hero), 'Шевченко Тарас Григорович')


class HeroViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        branch = Branch.objects.create(name='Збройні Сили України')
        cls.alpha = Hero.objects.create(
            full_name='Андрієнко Петро Іванович', branch=branch,
            rank_dates='(01.01.1980 – 02.02.2023)', biography='Перший абзац.\nДругий абзац.',
            birth_raion='Одеський',
        )
        cls.beta = Hero.objects.create(full_name='Бондаренко Іван Сергійович', branch=branch)
        cls.hidden = Hero.objects.create(full_name='Ярошенко Олег Петрович', is_published=False)

    def test_list_returns_published_heroes(self):
        response = self.client.get(reverse('heroes:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Андрієнко Петро Іванович')
        self.assertContains(response, 'Бондаренко Іван Сергійович')
        self.assertNotContains(response, 'Ярошенко Олег Петрович')

    def test_list_grouped_by_letter(self):
        response = self.client.get(reverse('heroes:list'))

        letters = [group['letter'] for group in response.context['groups']]
        self.assertEqual(letters, ['А', 'Б'])

    def test_list_search_filters_by_surname(self):
        response = self.client.get(reverse('heroes:list'), {'q': 'андр'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Андрієнко Петро Іванович')
        self.assertNotContains(response, 'Бондаренко Іван Сергійович')

    def test_list_search_without_results_shows_message(self):
        response = self.client.get(reverse('heroes:list'), {'q': 'Неіснуючий'})

        self.assertContains(response, 'Нічого не знайдено')
        self.assertEqual(response.context['found_count'], 0)

    def test_list_handles_hero_without_photo(self):
        response = self.client.get(reverse('heroes:list'))

        self.assertContains(response, 'ph/no-photo.jpg')

    def test_detail_page(self):
        response = self.client.get(self.alpha.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Андрієнко Петро Іванович')
        self.assertContains(response, 'Збройні Сили України')
        self.assertEqual(len(response.context['paragraphs']), 2)

    def test_detail_wraps_around_to_last_hero(self):
        response = self.client.get(self.alpha.get_absolute_url())

        self.assertEqual(response.context['prev_hero'].pk, self.beta.pk)

    def test_detail_hidden_hero_returns_404(self):
        response = self.client.get(self.hidden.get_absolute_url())

        self.assertEqual(response.status_code, 404)


class ThumbnailTests(TestCase):
    """Миниатюры для карточек списков: 500 полноразмерных фото — слишком много."""

    def setUp(self):
        import tempfile
        from pathlib import Path

        from PIL import Image

        self.tmp = Path(tempfile.mkdtemp())
        self.media = self.tmp / 'media'
        (self.media / 'heroes' / 'x').mkdir(parents=True)

        self.override = self.settings(MEDIA_ROOT=str(self.media))
        self.override.enable()
        self.addCleanup(self.override.disable)

        Image.new('RGB', (1200, 900), 'red').save(
            self.media / 'heroes' / 'x' / '1.jpg', format='JPEG',
        )

        self.hero = Hero.objects.create(full_name='Тестовий Герой')
        self.photo = HeroPhoto.objects.create(
            hero=self.hero, image='heroes/x/1.jpg', order=0,
        )

    def test_thumb_created_on_save(self):
        self.assertTrue(self.photo.thumb)
        self.assertTrue(self.photo.thumb.name.endswith('.jpg'))

    def test_thumb_is_smaller_than_original(self):
        self.assertLess(self.photo.thumb.size, self.photo.image.size)

    def test_thumb_fits_max_size(self):
        from PIL import Image

        with Image.open(self.photo.thumb.path) as img:
            self.assertLessEqual(max(img.size), 400)

    def test_thumb_url_falls_back_to_image(self):
        self.assertTrue(self.photo.thumb_url.endswith('/thumbs/1.jpg'))

        self.photo.thumb = ''
        self.assertEqual(self.photo.thumb_url, self.photo.image.url)

    def test_broken_image_does_not_break_save(self):
        (self.media / 'heroes' / 'x' / 'broken.jpg').write_bytes(b'not an image')

        photo = HeroPhoto.objects.create(
            hero=self.hero, image='heroes/x/broken.jpg', order=1,
        )

        self.assertFalse(photo.thumb)
