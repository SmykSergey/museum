from django.urls import path

from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.ProcurementListView.as_view(), name='list'),
]
