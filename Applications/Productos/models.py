from django.db import models

class Producto(models.Model):
    CATEGORIAS = [
        ('BIDON_COMPLETO', 'Bidón completo'),
        ('RECARGA', 'Recarga'),
        ('BOTELLA', 'Botella'),
        ('DISPENSADOR', 'Dispensador'),
    ]

    VOLUMENES = [
        ('20L', '20 litros'),
        ('10L', '10 litros'),
        ('1600CC', '1.600 cc'),
        ('1100CC', '1.100 cc'),
        ('600CC', '600 cc'),
        ('N/A', 'No aplica'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    volumen = models.CharField(max_length=10, choices=VOLUMENES, default='N/A')
    descripcion = models.TextField(blank=True, null=True)
    precio = models.PositiveIntegerField("Precio (CLP)")
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.get_volumen_display()}) - ${self.precio:,}"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['categoria', 'volumen', 'nombre']
