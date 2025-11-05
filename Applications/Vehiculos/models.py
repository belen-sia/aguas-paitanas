from django.db import models
from Applications.Repartidores.models import Repartidor

class Vehiculo(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"


class RepartidorVehiculo(models.Model):
    repartidor = models.ForeignKey(Repartidor, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.repartidor} -> {self.vehiculo} ({self.fecha_asignacion})"
