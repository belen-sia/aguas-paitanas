from django.db import models
from Applications.Productos.models import Producto
from Applications.Sucursales.models import  Sucursal


class Stock(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='stocks')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad_actual = models.IntegerField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre} ({self.cantidad_actual})"

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        ordering = ['producto', 'sucursal']