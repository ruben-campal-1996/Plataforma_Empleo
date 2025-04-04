from django.db import models
from django.conf import settings  # Importa settings

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('pendiente', 'Pendiente'),
    ])
    gestor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='proyectos_gestores')

    def __str__(self):
        return self.nombre

class Tarea(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='tareas', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    ])
    prioridad = models.CharField(max_length=10, choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ])
    colaborador = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tareas_colaboradores', blank=True)
    habilidades_requeridas = models.ManyToManyField('Analisis_mercado.Habilidad', related_name='tareas_habilidades')

    def __str__(self):
        return self.nombre