from django.db import models

class Sucursal(models.Model):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    ubicacion = models.CharField('Ubicación', max_length=50)

    def __str__(self):
        return f"{self.id} - {self.nombre} - {self.ubicacion}"