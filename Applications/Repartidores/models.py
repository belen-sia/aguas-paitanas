from django.db import models

class Repartidor(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    correo_electronico = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Repartidor"
        verbose_name_plural = "Repartidores"
        ordering = ['apellido', 'nombre']


class NotificacionRepartidor(models.Model):
    correo_electronico = models.EmailField()
    pedido_id = models.IntegerField()
    mensaje = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación #{self.id} para {self.correo_electronico}: {self.mensaje[:40]}..."

    class Meta:
        verbose_name = "Notificación de Repartidor"
        verbose_name_plural = "Notificaciones de Repartidores"
        ordering = ['-created_at']
