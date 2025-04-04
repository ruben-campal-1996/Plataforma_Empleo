from django.db import models

class OfertaEmpleo(models.Model):
    titulo = models.CharField(max_length=255)
    empresa = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    habilidades_requeridas = models.ManyToManyField('Habilidad', related_name='ofertas_habilidades')
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_publicacion = models.DateField()
    plataforma = models.CharField(max_length=50, choices=[
        ('tecnoempleo', 'Tecnoempleo'),
        ('infojobs', 'InfoJobs'),
        ('linkedin', 'LinkedIn'),
    ])

    def __str__(self):
        return f"{self.titulo} - {self.empresa}"

class Habilidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class TendenciaHabilidad(models.Model):
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    fecha = models.DateField()
    cantidad_ofertas = models.PositiveIntegerField()

    def __str__(self):
        return f"Tendencia de {self.habilidad.nombre} - {self.fecha}"