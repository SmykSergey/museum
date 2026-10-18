# Сайт музея

Django + PostgreSQL + Docker + i18n (uk/en).

**Проект:** Одеський історико-краєзнавчий музей (волонтёрский).
**Статус:** идёт разработка. Готовы каркас (этап 1) и раздел «Герої не вмирають».

## Стек

- Python 3.14, Django 6.1
- PostgreSQL 16 (в Docker)
- django-modeltranslation (i18n моделей)
- django-ckeditor-5 (rich-text)
- python-dotenv (конфигурация)

## Структура

```
museum/
├── backend/                 # Django-проект
│   ├── config/              # настройки (base/dev/prod)
│   ├── apps/
│   │   ├── core/            # главная страница, общие утилиты (utils.py)
│   │   ├── news/            # новости
│   │   ├── events/          # события и архив
│   │   ├── locations/       # 4 локации
│   │   ├── pages/           # «Про музей» и «Історія музею» (синглтоны)
│   │   ├── exhibits/        # експонати (розділ «Експозиція»)
│   │   ├── library/         # бібліотека («Вісник музею»)
│   │   ├── procurement/     # державні закупівлі
│   │   └── heroes/          # «Герої не вмирають»
│   │       └── data/        # heroes-data.json — исходные данные раздела
│   ├── templates/           # base.html
│   ├── static/              # css/, js/, ph/
│   ├── locale/              # переводы uk/en (этап 5)
│   └── media/               # загруженные фото (в git не хранится)
└── docker-compose.yml       # позже, для прода (этап 7)
```

## Что уже работает

| Раздел | Адрес | Статус |
|---|---|---|
| Главная | `/` | данные из БД: локации, события, новости |
| Про музей | `/about/` | фото, карточки-разделы, экспозиция, контакты, карта |
| Історія музею | `/about/history/` | текст и архивные фото |
| Експонат | `/exhibits/<slug>/` | фото и описание экспоната |
| Бібліотека | `/library/` | 21 выпуск «Вісника», поиск по номеру и названию |
| Державні закупівлі | `/procurement/` | документы по годам, фильтр и поиск |
| Герои | `/geroi/`, `/geroi/<slug>/` | 500 записей, поиск, алфавит, галерея |
| Новости | `/news/`, `/news/<slug>/` | список с пагинацией, страница новости |
| События | `/events/`, `/events/archive/`, `/events/<slug>/` | актуальные, архив, страница события |
| Локации | `/locations/`, `/locations/<slug>/` | график, цены, события площадки |
| Админка | `/admin/` | все разделы с переводами, превью и фильтрами |

Готовы этапы 0–4 (включая 4.5–4.7: герои, дополнительные страницы, API и
киоск) плана `to-do.md`. Дальше — этап 5 (переводы uk/en).

- Гайд по обновлению данных и киоска: `docs/kiosk-guide.md`
- Промты для дизайна новых страниц: `docs/figma-prompts.md`

## Общие утилиты

`apps/core/utils.py`:

- `transliterate_uk()` — транслитерация по постановлению КМУ № 55
  («Шевченко Тарас» → «Shevchenko Taras») для автоматических адресов страниц;
- `make_sort_key()` — ключ правильной украинской сортировки: PostgreSQL
  сортирует кириллицу по байтам, из-за чего і, ї, є, ґ встают не на место.

## Фото героев

Файлы фото (1003 шт., ~178 МБ) **не хранятся в git** — они лежат:
- в `backend/media/heroes/<slug>/` — то, что отдаёт сайт (папка в `.gitignore`);
- во внешнем архиве (папка `museum_page/` с макетом киоска) — резервная копия
  и источник для импорта с нуля.

Исходная вёрстка (`frontend/`) удалена как дубль: она целиком перенесена в
`backend/templates/`, `backend/static/` и `backend/media/`.

Чтобы развернуть фото из архива, распакуйте его в `frontend/heroes-photos/`
(структура `<id>/<номер>.jpg`) и запустите `python manage.py import_heroes`.

## Локальный запуск

### 1. PostgreSQL в Docker

> **Важно:** на этой машине порты 5432 и 5433 заняты другими проектами
> (`dt-timescaledb`, `biosgis-db`), поэтому музейный Postgres проброшен на **5440**.
> Если порт снова окажется занят — выберите свободный (`ss -ltn`) и поправьте
> `POSTGRES_PORT` в `.env`.

```bash
docker run -d --name museum-postgres \
  -e POSTGRES_USER=museum \
  -e POSTGRES_PASSWORD=museum_dev_pass \
  -e POSTGRES_DB=museum \
  -p 5440:5432 \
  -v museum_pg_data:/var/lib/postgresql/data \
  postgres:16
```

Проверить: `docker ps | grep museum-postgres`

### 2. venv и зависимости

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Переменные окружения

```bash
cp .env.example .env
# отредактируйте SECRET_KEY и POSTGRES_PORT (по умолчанию 5440)
```

### 4. Миграции и данные

```bash
python manage.py migrate
python manage.py seed_demo                    # все демо-данные для разработки
python manage.py import_heroes --skip-photos  # если фото героев уже лежат в media/
# или
python manage.py import_heroes                # если распакован архив фото
```

### 5. Запуск

```bash
python manage.py runserver 8010
```

> Порт 8000 на этой машине занят контейнером `dt-backend` из другого проекта,
> поэтому используется **8010**.

- Сайт: http://127.0.0.1:8010/
- Раздел «Герої не вмирають»: http://127.0.0.1:8010/geroi/
- Админка: http://127.0.0.1:8010/admin/ (локальный пользователь `admin`)

## Раздел «Герої не вмирають»

310 записей перенесены из статического `frontend/heroes-data.json` в базу данных.

- Список: `/geroi/` — серверный рендер, группировка по буквам, алфавитный указатель,
  поиск по фамилии (`/geroi/?q=Іванов`), мгновенный фильтр карточек на JS.
- Страница героя: `/geroi/<id>/` — фото, биография, галерея с лайтбоксом,
  переход к соседним записям.
- Сортировка по-украински: поле `Hero.sort_key` (PostgreSQL сортирует кириллицу
  по байтам, а не по алфавиту, поэтому порядок букв считается в Python).

### Повторный импорт

```bash
python manage.py import_heroes --dry-run        # только отчёт
python manage.py import_heroes --skip-photos    # обновить данные, фото уже в media/
python manage.py import_heroes --photos /путь   # фото лежат в другом месте
python manage.py import_heroes --heroes Ivanov_Valerii_Anatoliiovych
```

Команда обновляет существующие записи по `slug` и пересобирает галерею,
поэтому её можно запускать повторно без создания дублей.

Если папка с фото не найдена, команда останавливается с ошибкой и ничего не
меняет в базе — чтобы случайно не удалить записи о фото.


## API для киоска

Сайт — единственный источник данных. Киоск (сенсорный стол) забирает данные
через read-only API и хранит локальную копию, поэтому работает без интернета.

Базовый адрес: `/api/v1/`

| Метод | Что отдаёт |
|---|---|
| `GET /api/v1/ping/` | статус, версия набора данных, счётчики |
| `GET /api/v1/branches/` | роды войск с количеством героев |
| `GET /api/v1/districts/` | районы Одещины + ссылка на карту района |
| `GET /api/v1/heroes/` | список героев; фильтры `period`, `branch`, `district`, `q`, `limit`, `offset` |
| `GET /api/v1/heroes/<slug>/` | карточка героя: биография, галерея, карта района |
| `GET /api/v1/sync/` | полный набор данных + манифест файлов (sha256) |

Ответы сжимаются gzip (sync: 968 КБ → 113 КБ), поддерживается `ETag`
и `If-None-Match` (304), а `?since=<версия>` возвращает `not_modified`.

## Сборка киоска

```bash
python manage.py build_kiosk                    # ~170 МБ, с разделом 2014–2021
python manage.py build_kiosk --no-legacy        # ~62 МБ, только 2022+
python manage.py build_kiosk --out /media/usb/kiosk --photos original
```

Команда собирает в `dist/kiosk/` готовую папку: 500 карточек героев, списки по
родам войск, `soldiers_data.js`, `data.json`, `sync.json`, фото (сжатые до
1000 px, качество 80) и карты районов. В конце проверяет, что все локальные
ссылки ведут на существующие файлы.

Папку достаточно целиком скопировать на сенсорный стол.

## Полезные команды

```bash
python manage.py check               # проверка конфигурации
python manage.py test                # тесты (46 шт.)
python manage.py makemigrations      # новые миграции
python manage.py createsuperuser     # новый администратор
python manage.py seed_demo --clear   # пересоздать демо-данные
python manage.py collectstatic       # сбор статики (этап 6)
```

## Что дальше

См. `to-do.md`. Этапы 0–4 и раздел «Герої не вмирають» готовы.
Ближайший шаг — **этап 5**: переводы uk/en (интерфейс через `{% trans %}` уже
размечен, нужны `.po`-файлы и английские тексты в моделях).
