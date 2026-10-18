from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    # 'archive/' должен идти раньше '<slug>/', иначе архив примут за slug
    path('archive/', views.EventArchiveView.as_view(), name='archive'),
    path('<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
]
