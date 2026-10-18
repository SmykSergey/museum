from django.urls import path

from . import views

app_name = 'exhibits'

urlpatterns = [
    path('<slug:slug>/', views.ExhibitDetailView.as_view(), name='detail'),
]
