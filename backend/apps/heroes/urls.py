from django.urls import path

from . import views

app_name = 'heroes'

urlpatterns = [
    path('', views.hero_list, name='list'),
    path('<slug:slug>/', views.hero_detail, name='detail'),
]
