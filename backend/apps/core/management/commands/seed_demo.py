"""Тестовые данные для локальной разработки.

Заполняет базу реальными данными четырёх площадок музея (взяты из вёрстки),
новостями, событиями, экспонатами, выпусками библиотеки и документами
закупок — чтобы было видно, как работает сайт.

    python manage.py seed_demo            # создать (повторный запуск ничего не ломает)
    python manage.py seed_demo --clear    # удалить созданное и создать заново

На продакшене команду запускать не нужно — там данные вводят через админку.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.events.models import Event
from apps.exhibits.models import Exhibit
from apps.library.models import LibraryIssue
from apps.locations.models import Location
from apps.news.models import NewsItem
from apps.pages.models import AboutPage, HistoryPage
from apps.procurement.models import ProcurementDocument

# название, адрес, фото из static/ph, график работы
LOCATIONS = [
    {
        'name': 'Одеський історико-краєзнавчий музей',
        'address': 'вул. Гаванна, 4',
        'photo': 'gavanna.jpg',
        'schedule': 'Пн–Пт: 10:00 – 18:00\nСб: 10:00 – 17:00\nНд: вихідний',
        'order': 10,
        'prices': '<p>Дорослий квиток — 100 ₴<br>Студенти — 50 ₴<br>Школярі — 30 ₴</p>',
        'description': (
            '<p>Одеський історико-краєзнавчий музей — одна з найстаріших '
            'наукових установ міста. Тут зберігається понад 300 тисяч '
            'експонатів, які розповідають історію Одещини від найдавніших '
            'часів до сьогодення.</p>'
        ),
    },
    {
        'name': 'Музей Степова Україна',
        'address': 'вул. Ланжеронівська 24-а',
        'photo': 'lanzheron.jpg',
        'schedule': 'Пн–Пт: 10:00 – 18:00\nСб–Нд: вихідні',
        'order': 20,
        'prices': '<p>Дорослий квиток — 80 ₴<br>Студенти — 40 ₴</p>',
        'description': (
            '<p>Експозиція присвячена історії та етнографії степової частини '
            'Одещини: побут, ремесла і культура народів регіону.</p>'
        ),
    },
    {
        'name': 'Меморіал героїчної оборони Одеси 411-ї берегової батареї',
        'address': 'вулиця Дача Ковалевського, 150',
        'photo': 'kovalevskogo.jpg',
        'schedule': 'Пн–Нд: 09:00 – 18:00',
        'order': 30,
        'prices': '<p>Вхід вільний</p>',
        'description': (
            '<p>Меморіал на місці легендарної 411-ї берегової батареї, яка '
            'тримала оборону Одеси у 1941 році.</p>'
        ),
    },
    {
        'name': 'Болградський історико-етнографічний музей',
        'address': 'проспект Соборний, 154, м. Болград',
        'photo': 'soborn.jpg',
        'schedule': 'Пн–Пт: 09:00 – 17:00\nСб: 10:00 – 15:00',
        'order': 40,
        'prices': '<p>Дорослий квиток — 60 ₴<br>Діти — 20 ₴</p>',
        'description': (
            '<p>Музей розповідає про історію та культуру болгарської '
            'громади Бессарабії.</p>'
        ),
    },
]

NEWS = [
    {
        'title': 'Відкриття виставки «Одеса: сто років потому»',
        'summary': 'Нова експозиція з рідкісними світлинами міста початку XX століття.',
        'body': '<p>Запрошуємо на відкриття виставки, присвяченої архітектурі '
                'та побуту Одеси початку минулого століття.</p>',
        'days_ago': 2,
    },
    {
        'title': 'Музей отримав унікальний архів родини Ковалевських',
        'summary': 'Понад 200 документів, листів і фотографій передано до фондів музею.',
        'body': '<p>Архів передано нащадками родини. Найближчим часом '
                'матеріали буде описано та оцифровано.</p>',
        'days_ago': 9,
    },
    {
        'title': 'Зміна графіка роботи у святкові дні',
        'summary': 'Просимо звернути увагу на оновлений графік роботи локацій.',
        'body': '<p>У святкові дні музеї працюватимуть за скороченим графіком.</p>',
        'days_ago': 20,
    },
]

EVENTS = [
    {
        'title': 'Екскурсія «Таємниці одеських дворів»',
        'summary': 'Пішохідна екскурсія історичним центром міста.',
        'body': '<p>Тривалість — 2 години. Збір біля головного входу музею.</p>',
        'days_ahead': 5,
        'location_index': 0,
    },
    {
        'title': 'Лекція «Степові культури Північного Причорномор’я»',
        'summary': 'Наукова лекція для всіх охочих.',
        'body': '<p>Читає провідний науковий співробітник музею.</p>',
        'days_ahead': 12,
        'location_index': 1,
    },
    {
        'title': 'День пам’яті захисників Одеси',
        'summary': 'Меморіальний захід біля 411-ї берегової батареї.',
        'body': '<p>Покладання квітів, екскурсія меморіалом.</p>',
        'days_ahead': 30,
        'location_index': 2,
    },
    {
        'title': 'Виставка дитячого малюнка «Моє місто»',
        'summary': 'Роботи юних художників Одещини.',
        'body': '<p>Виставка проходила у травні та завершилася.</p>',
        'days_ahead': -25,
        'location_index': 0,
    },
]

# документы из макета (procurement.html): (дата ДД.ММ.ГГГГ, название)
PROCUREMENT_DOCS = [
    ('21.01.2026', 'Річний план КУ ОІКМ на 2026 рік'),
    ('23.01.2026', 'Зміни до річного плану КУ ОІКМ'),
    ('02.02.2026', 'Обґрунтування технічних та якісних характеристик закупівлі електричної енергії'),
    ('19.02.2026', 'Зміни до річного плану КУ ОІКМ'),
    ('04.03.2026', 'Обґрунтування закупівлі послуг теплопостачання'),
    ('12.03.2026', 'Обґрунтування послуг з охорони'),
    ('14.02.2025', 'Зміни до річного плану КУ ОІКМ на 2025 рік'),
    ('18.03.2025', 'Обґрунтування закупівлі послуг з розподілу електричної енергії'),
    ('10.06.2025', 'Обґрунтування закупівлі послуг теплопостачання'),
    ('24.11.2025', 'Зміни до річного плану КУ ОІКМ'),
    ('05.12.2025', 'Зміни до річного плану КУ ОІКМ'),
    ('12.12.2025', 'Обґрунтування послуг з охорони'),
    ('22.12.2025', 'Зміни до річного плану КУ ОІКМ'),
    ('16.01.2024', 'Річний план КУ ОІКМ на 2024 рік'),
    ('29.01.2024', 'Зміни до річного плану КУ ОІКМ'),
    ('08.02.2024', 'Обґрунтування технічних та якісних характеристик закупівлі електричної енергії'),
    ('26.02.2024', 'Обґрунтування закупівлі послуг теплопостачання'),
    ('14.03.2024', 'Зміни до річного плану КУ ОІКМ'),
    ('02.04.2024', 'Обґрунтування послуг з охорони'),
    ('21.05.2024', 'Обґрунтування закупівлі послуг з розподілу електричної енергії'),
    ('17.07.2024', 'Зміни до річного плану КУ ОІКМ'),
    ('09.09.2024', 'Зміни до річного плану КУ ОІКМ'),
    ('28.10.2024', 'Обґрунтування закупівлі послуг теплопостачання'),
    ('19.12.2024', 'Зміни до річного плану КУ ОІКМ'),
]

# текст страницы «Історія музею» из макета
HISTORY_PARAGRAPHS = [
    'Вперше музейна експозиція розмістилася тут в 1948 році. Це була виставка «Героїчна оборона Одеси», на основі якої згодом створили республіканський Музей оборони Одеси.',
    '6 травня 1956 року гостинно відчинив двері своїм першим відвідувачам Одеський державний історико-краєзнавчий музей. Він був сформований на базі Музею оборони Одеси та Одеського обласного краєзнавчого музею. Документи, друковані видання, предмети прикладного та образотворчого мистецтва, нумізматичні колекції XVII–XIX століть, пов\'язані з історією міста і краю і колись входили до зібрання Музею Одеського товариства історії та старожитностей, Музею книги, Музею Старої Одеси і деяких інших, виявилися складовою частиною його фондів.',
    'У 1983 році музей закрився на капітальний ремонт, який тривав довгих одинадцять років. В результаті силами Одеських художньо-реставраційних майстерень палацові інтер\'єри особняка були відновлені в своєму первозданному вигляді.',
]

# ссылка на карту из макета (атрибут src у iframe)
ABOUT_MAP_URL = 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2747.1083666330815!2d30.735984600000002!3d46.4861666!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40c631bd889d7a39%3A0x320a724d00e05291!2z0J7QtNC10YHRgdC60LjQuSDQuNGB0YLQvtGA0LjQutC-LdC60YDQsNC10LLQtdC00YfQtdGB0LrQuNC5INCc0YPQt9C10Lk!5e0!3m2!1suk!2sua!4v1791498512003!5m2!1suk!2sua'

# единственный готовый экспонат из макета
EXHIBIT = {
    'title': 'Шолом типу «Моріон», XVII століття',
    'image': 'ph/expo/morion.jpg',
    'summary': 'Колекція зброї музею',
    'body': '<p>Цей шолом є яскравим зразком європейського захисного озброєння пізнього Середньовіччя та початку Нового часу. Завдяки своєму високому гребеню та вигнутим полям, моріон не лише надійно захищав голову воїна, а й слугував символом статусу свого власника. Майстерне карбування на поверхні шолома свідчить про високий рівень ковальського мистецтва тієї епохи.</p>',
    'order': 10,
}

# в макете библиотека содержит 21 выпуск-заглушку
LIBRARY_ISSUES = 21

class Command(BaseCommand):
    help = 'Создаёт демонстрационные локации, новости и события'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Удалить ранее созданные демо-записи перед созданием новых',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Event.objects.filter(title__in=[e['title'] for e in EVENTS]).delete()
            NewsItem.objects.filter(title__in=[n['title'] for n in NEWS]).delete()
            Location.objects.filter(name__in=[l['name'] for l in LOCATIONS]).delete()
            self.stdout.write('Старые демо-записи удалены.')

        locations = self._create_locations()

        news_created = 0
        for item in NEWS:
            _, created = NewsItem.objects.update_or_create(
                title=item['title'],
                defaults={
                    'summary': item['summary'],
                    'body': item['body'],
                    'published_at': timezone.now() - timedelta(days=item['days_ago']),
                    'is_published': True,
                },
            )
            news_created += created

        events_created = 0
        for item in EVENTS:
            _, created = Event.objects.update_or_create(
                title=item['title'],
                defaults={
                    'summary': item['summary'],
                    'body': item['body'],
                    'starts_at': timezone.now() + timedelta(days=item['days_ahead']),
                    'location': locations[item['location_index']],
                    'is_published': True,
                    'is_archived': False,
                },
            )
            events_created += created

        self._create_pages(locations)
        self._create_exhibit()
        issues_created = self._create_library()
        docs_created = self._create_procurement()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Демо-данные готовы:'))
        self.stdout.write('  локацій всего: %s' % Location.objects.count())
        self.stdout.write('  новин создано: %s (всего %s)' % (news_created, NewsItem.objects.count()))
        self.stdout.write('  подій создано: %s (всего %s)' % (events_created, Event.objects.count()))
        self.stdout.write('  експонатів: %s' % Exhibit.objects.count())
        self.stdout.write('  випусків бібліотеки: %s (создано %s)' % (
            LibraryIssue.objects.count(), issues_created))
        self.stdout.write('  документів закупівель: %s (создано %s)' % (
            ProcurementDocument.objects.count(), docs_created))
        self.stdout.write('  сторінки «Про музей» і «Історія музею»: готовы')

    def _create_pages(self, locations):
        """Заполняет единственные страницы «Про музей» и «Історія музею»."""
        about = AboutPage.load()
        about.title = 'Про музей'
        about.subtitle = 'Одеський історико-краєзнавчий музей'
        about.main_location = locations[0]
        about.map_embed_url = ABOUT_MAP_URL
        if not about.photo:
            about.photo = self._copy_static_image('pages/gavanna.jpg', 'gavanna.jpg') or ''
        about.save()

        history = HistoryPage.load()
        history.title = 'Історія музею'
        history.body = ''.join('<p>%s</p>' % text for text in HISTORY_PARAGRAPHS)
        if not history.photo_1:
            history.photo_1 = self._copy_static_image('pages/history1.png', 'history1.png') or ''
        if not history.photo_2:
            history.photo_2 = self._copy_static_image('pages/history2.png', 'history2.png') or ''
        history.save()

    def _create_exhibit(self):
        """Создаёт экспонат из макета и копирует его фото в media."""
        exhibit, _ = Exhibit.objects.update_or_create(
            title=EXHIBIT['title'],
            defaults={
                'summary': EXHIBIT['summary'],
                'body': EXHIBIT['body'],
                'order': EXHIBIT['order'],
                'is_published': True,
            },
        )
        if not exhibit.image:
            # 'ph/expo/morion.jpg' -> 'expo/morion.jpg' внутри static/ph
            filename = EXHIBIT['image'].split('/', 1)[-1]
            exhibit.image = self._copy_static_image('exhibits/morion.jpg', filename) or ''
            exhibit.save(update_fields=['image'])
        return exhibit

    def _create_library(self):
        """Создаёт выпуски «Вісника» — в макете их 21."""
        created = 0
        for number in range(1, LIBRARY_ISSUES + 1):
            _, was_created = LibraryIssue.objects.get_or_create(
                number=number,
                defaults={'title': 'Вісник музею', 'is_published': True},
            )
            created += was_created
        return created

    def _create_procurement(self):
        """Создаёт документы закупок из макета."""
        created = 0
        for date_text, title in PROCUREMENT_DOCS:
            date = datetime.strptime(date_text, '%d.%m.%Y').date()
            _, was_created = ProcurementDocument.objects.get_or_create(
                date=date,
                title=title,
                defaults={'is_published': True},
            )
            created += was_created
        return created

    def _create_locations(self):
        """Создаёт локации и подкладывает им фото из static/ph."""
        locations = []
        for item in LOCATIONS:
            location, _ = Location.objects.update_or_create(
                name=item['name'],
                defaults={
                    'address': item['address'],
                    'schedule': item['schedule'],
                    'prices': item['prices'],
                    'description': item['description'],
                    'order': item['order'],
                    'is_published': True,
                },
            )
            self._attach_photo(location, item['photo'])
            locations.append(location)
        return locations

    def _attach_photo(self, location, filename):
        """Копирует фото из static/ph в media и привязывает к локации."""
        if location.photo:
            return

        relative = self._copy_static_image('locations/%s' % filename, filename)
        if relative:
            location.photo = relative
            location.save(update_fields=['photo'])

    def _copy_static_image(self, media_relative, static_filename):
        """Копирует файл из static/ph в MEDIA_ROOT и возвращает путь для поля ImageField.

        media_relative — путь внутри media без имени файла-источника,
        например 'pages/gavanna.jpg' или 'exhibits/morion.jpg'.
        static_filename — файл в static/ph, например 'gavanna.jpg' или 'expo/morion.jpg'.
        """
        source = Path(settings.BASE_DIR) / 'static' / 'ph' / static_filename
        if not source.exists():
            self.stderr.write('  ! нет файла: %s' % source)
            return ''

        target = Path(settings.MEDIA_ROOT) / media_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)

        return media_relative
