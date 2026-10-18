from django.urls import path

from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.LocationListView.as_view(), name='list'),
    path('<slug:slug>/', views.LocationDetailView.as_view(), name='detail'),
]
