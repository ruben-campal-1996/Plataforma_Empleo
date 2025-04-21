from django.urls import path
from . import views


app_name = 'Recomendacion_IA'

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('get_chat_history/', views.get_chat_history, name='get_chat_history'),
]