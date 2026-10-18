from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('', views.ping, name='ping'),
    path('ping/', views.ping, name='ping-explicit'),
    path('branches/', views.branches, name='branches'),
    path('districts/', views.districts, name='districts'),
    path('heroes/', views.hero_list, name='heroes'),
    path('heroes/<slug:slug>/', views.hero_detail, name='hero-detail'),
    path('sync/', views.sync, name='sync'),
    path('bundle/', views.bundle, name='bundle'),
]
