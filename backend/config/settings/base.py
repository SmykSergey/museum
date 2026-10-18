"""
Базовые настройки проекта (общие для dev и prod).

Структура:
    config/settings/base.py  — этот файл, всё общее
    config/settings/dev.py   — локальная разработка
    config/settings/prod.py  — продакшен
    config/settings/__init__.py — выбирает dev/prod по DJANGO_ENV
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# backend/config/settings/base.py -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')


# ===== Безопасность =====

# Секретный ключ обязателен: он задаётся в .env (см. .env.example).
SECRET_KEY = os.getenv('SECRET_KEY', '')

# Переопределяется в dev.py / prod.py.
DEBUG = False

ALLOWED_HOSTS = []


# ===== Приложения =====

INSTALLED_APPS = [
    # modeltranslation обязан идти до django.contrib.admin
    'modeltranslation',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_ckeditor_5',

    # локальные приложения
    'apps.core',
    'apps.news',
    'apps.events',
    'apps.locations',
    'apps.heroes',
    'apps.pages',
    'apps.exhibits',
    'apps.library',
    'apps.procurement',
    'apps.api',
    'apps.kiosk',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # сжатие ответов: JSON для киоска весит мегабайты
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # LocaleMiddleware строго после SessionMiddleware и до CommonMiddleware
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ===== База данных =====

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'museum'),
        'USER': os.getenv('POSTGRES_USER', 'museum'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===== Пароли =====

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===== Локализация =====

LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('uk', 'Українська'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# django-modeltranslation: украинский — основной язык, английский — перевод
MODELTRANSLATION_DEFAULT_LANGUAGE = 'uk'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('uk', 'en')
# без этого modeltranslation не умеет переводить поля CKEditor
MODELTRANSLATION_CUSTOM_FIELDS = ('CKEditor5Field',)


# ===== Статика и медиа =====

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ===== Почта =====

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'museum@example.com')


# ===== Киоск =====
# Папка с готовыми страницами киоска (portal.html, start_2022.html, style.css).
# Сборка `build_kiosk` берёт оттуда каркас и подменяет данные на наши.
KIOSK_DESIGN_DIR = os.getenv('KIOSK_DESIGN_DIR', str(BASE_DIR.parent / 'museum_page'))

# Готовый архив киоска: его скачивает стол при синхронизации (/api/v1/bundle/).
# Создаётся командой `python manage.py build_kiosk --zip`.
KIOSK_BUNDLE_PATH = os.getenv('KIOSK_BUNDLE_PATH', str(BASE_DIR.parent / 'dist' / 'kiosk.zip'))


# ===== CKEditor 5 =====


CKEDITOR_5_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
CKEDITOR_5_UPLOAD_PATH = 'uploads/'

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|',
            'blockQuote', 'insertTable', '|',
            'undo', 'redo',
        ],
        'language': 'uk',
    },
}
