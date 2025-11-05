from django.db import models
from Applications.Sucursales.models import Sucursal
# Create your models here.
class Trabajadores(models.Model):

    opciones_cargo = (
        ('0', 'Administrador'),
        ('1', 'Repartidor'),
        ('2', 'Operario de Planta'),
        ('3', 'Otro'),
    )

    nombre = models.CharField('Nombre', max_length=60)
    apellido = models.CharField('Apellido', max_length=60)
    nombre_completo = models.CharField(
        'Nombre Completo',
        max_length=60,
        blank=True
    )
    correo_electronico = models.EmailField('Correo Electrónico', max_length=50)
    cargo = models.CharField('Cargo', max_length=1, choices=opciones_cargo)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    telefono = models.CharField('Teléfono', max_length=20)
    contrasena = models.CharField('Contraseña', max_length=20)

    def __str__(self):
        return str(self.id) + '-' + self.nombre + ' ' + self.apellido + ' ' + self.correo_electronico + ' ' + self.cargo + ' ' + str(self.sucursal) + ' ' + self.telefono + ' ' + self.contrasena
        