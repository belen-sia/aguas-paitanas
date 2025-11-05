from django.db import models
from Applications.Productos.models import Producto
from Applications.Sucursales.models import Sucursal

class Merma(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='mermas')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=100)
    costo = models.FloatField()
    fecha = models.DateField(auto_now_add=True)  # se asigna automáticamente al crear

    def __str__(self):
        return f"{self.producto.nombre} - {self.motivo}"
