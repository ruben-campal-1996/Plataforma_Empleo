import os
from celery import Celery

# Configurar el módulo de ajustes por defecto para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Plataforma.settings')

app = Celery('Plataforma')

# Cargar la configuración de Celery desde los ajustes de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir tareas automáticamente en las aplicaciones instaladas
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')