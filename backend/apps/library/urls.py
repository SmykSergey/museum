from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.LibraryListView.as_view(), name='list'),
]
