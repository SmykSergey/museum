"""Настройки для локальной разработки."""

import os

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,[::1]').split(',')

# В dev-режиме секретный ключ может отсутствовать — подставляем небезопасный,
# чтобы runserver не падал у нового разработчика до создания .env.
if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = 'django-insecure-dev-only-ne-zapuskat-v-prod'

INTERNAL_IPS = ['127.0.0.1']

# Позже добавим сюда django-debug-toolbar, если понадобится
