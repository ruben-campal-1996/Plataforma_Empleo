from django.db import models
from django.conf import settings  # Importa settings
from Proyectos.models import Tarea

class Recomendacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recomendaciones")
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="recomendaciones")
    puntuacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_recomendacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Recomendación para {self.usuario.username} - {self.tarea.nombre}"

class Prediccion(models.Model):
    habilidad = models.CharField(max_length=100)
    prediccion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_prediccion = models.DateField()

    def __str__(self):
        return f"Predicción de habilidad: {self.habilidad} - {self.fecha_prediccion}"
