"""Корневая конфигурация URL проекта."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('i18n/', include('django.conf.urls.i18n')),

    path('api/v1/', include('apps.api.urls')),

    path('geroi/', include('apps.heroes.urls')),
    path('news/', include('apps.news.urls')),
    path('events/', include('apps.events.urls')),
    path('locations/', include('apps.locations.urls')),
    path('about/', include('apps.pages.urls')),
    path('exhibits/', include('apps.exhibits.urls')),
    path('library/', include('apps.library.urls')),
    path('procurement/', include('apps.procurement.urls')),
    path('', include('apps.core.urls')),
]

# В разработке Django сам отдаёт загруженные файлы (в продакшене это делает Nginx).
# Статику в dev-режиме отдаёт django.contrib.staticfiles, её сюда добавлять не нужно.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
