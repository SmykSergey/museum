import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# Позже добавим сюда django-debug-toolbar, если понадобится