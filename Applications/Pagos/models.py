from django.db import models
from Applications.Pedidos.models import Pedido

class MetodoPago(models.Model):
    TIPO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('DEBITO', 'Debito'),
        ('CREDITO', 'Credito'),
    ]
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES)

    def __str__(self):
        return self.tipo_pago

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"


class TipoFacturacion(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('GUIA', 'Guia'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='facturaciones'
    )
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=30, unique=True)
    fecha_emision = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_documento} N°{self.numero_documento}"

    class Meta:
        verbose_name = "Tipo de Facturación"
        verbose_name_plural = "Tipos de Facturación"
        ordering = ['fecha_emision']


class Pago(models.Model):
    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos'
    )
    facturacion = models.ForeignKey(
        TipoFacturacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos'
    )
    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')

    def __str__(self):
        return f"Pago {self.id} - {self.estado} - ${self.monto}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['fecha']
