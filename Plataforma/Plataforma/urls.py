from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from Usuarios.views import index
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', lambda request: redirect('usuarios:index')),
    path('admin/', admin.site.urls),
    path('index/', include('Usuarios.urls')),  # URLs de la aplicación Usuarios
    #path('proyectos/', include('Proyectos.urls')),  # URLs de la aplicación Proyectos
    #path('integracion_datos/', include('Integracion_datos.urls')),  # URLs de la aplicación Integracion_datos
    #path('recomendacion_ia/', include('Recomendacion_IA.urls')),  # URLs de la aplicación Recomendacion_IA
    #path('analisis_mercado/', include('Analisis_mercado.urls')),  # URLs de la aplicación Analisis_mercado
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)