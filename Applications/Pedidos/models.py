from django.db import models
from Applications.Clientes.models import Cliente
from Applications.Repartidores.models import Repartidor
from Applications.Productos.models import Producto

class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En proceso'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    # Cliente existente (opcional para pedidos rápidos)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        related_name='pedidos',
        null=True,
        blank=True
    )

    # Campos para cliente rápido (solo para mostrar)
    nombre_cliente_temp = models.CharField(max_length=100, blank=True, null=True)
    apellido_cliente_temp = models.CharField(max_length=100, blank=True, null=True)
    direccion_temp = models.CharField(max_length=255, blank=True, null=True)
    telefono_temp = models.CharField(max_length=50, blank=True, null=True)

    tipo_cliente = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('Domiciliario', 'Domiciliario'),
            ('Empresa', 'Empresa'),
        ]
    )

    repartidor = models.ForeignKey(
        Repartidor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos'
    )
    fecha_pedido = models.DateField(auto_now_add=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        if self.cliente:
            return f"Pedido {self.id} - Cliente: {self.cliente.nombre} ({self.estado})"
        else:
            return f"Pedido {self.id} - Cliente rápido: {self.nombre_cliente_temp} ({self.estado})"

    def actualizar_monto_total(self):
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.monto_total = total
        self.save(update_fields=['monto_total'])

    def save(self, *args, **kwargs):
        # Si el pedido tiene un cliente asignado y aún no tiene tipo_cliente definido,
        # copiamos el tipo del cliente (D = Domiciliario, E = Empresa)
        if self.cliente and not self.tipo_cliente:
            if self.cliente.tipo_cliente == 'D':
                self.tipo_cliente = 'Domiciliario'
            elif self.cliente.tipo_cliente == 'E':
                self.tipo_cliente = 'Empresa'

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='detalles_pedido'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calcula subtotal automáticamente antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualiza el monto total del pedido
        self.pedido.actualizar_monto_total()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} (Pedido {self.pedido.id})"

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
        ordering = ['pedido']


