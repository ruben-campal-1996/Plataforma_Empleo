from django.db import models

class FuenteDatos(models.Model):
    nombre = models.CharField(max_length=255)
    url_api = models.URLField()
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class RegistroImportacion(models.Model):
    fuente = models.ForeignKey(FuenteDatos, on_delete=models.CASCADE)
    fecha_importacion = models.DateTimeField(auto_now_add=True)
    cantidad_ofertas = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=[
        ('exito', 'Éxito'),
        ('fallido', 'Fallido'),
    ])

    def __str__(self):
        return f"Importación desde {self.fuente.nombre} - {self.fecha_importacion}"