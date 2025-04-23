from django.db import models
from Usuarios.models import Usuario

class ConsultaBusqueda(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    palabra_clave = models.CharField(max_length=255)
    provincia = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    plataforma = models.CharField(max_length=50, choices=[('infojobs', 'InfoJobs'), ('tecnoempleo', 'Tecnoempleo')])

    def __str__(self):
        return f"{self.palabra_clave} - {self.provincia} ({self.fecha})"