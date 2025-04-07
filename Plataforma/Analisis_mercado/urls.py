from django.urls import path
from . import views

app_name = 'Analisis_mercado'

urlpatterns = [
    path('', views.index, name='index'),  # Página principal
    path('buscar_trabajos/', views.buscar_trabajos, name='buscar_trabajos'),
]