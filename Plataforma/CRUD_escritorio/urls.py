from django.urls import path
from . import views

app_name = 'CRUD_escritorio'

urlpatterns = [
    path('analisis/', views.analisis_view, name='analisis'),
    path('graficos/', views.graficos_view, name='graficos'),
    path('proyectos/', views.proyectos_view, name='proyectos'),
]