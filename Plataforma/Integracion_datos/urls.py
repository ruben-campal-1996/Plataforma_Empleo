from django.urls import path
from . import views

app_name = 'integracion_datos'

urlpatterns = [
    path('', views.index, name='index'),  # Vista de ejemplo
]