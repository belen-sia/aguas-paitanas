from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Cliente(models.Model):
    TIPO_CLIENTE = [
        ('D', 'Domiciliario'),
        ('E', 'Empresa'),
    ]

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)  # formato +569XXXXXXXX
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=255)
    tipo_cliente = models.CharField(max_length=1, choices=TIPO_CLIENTE)
    fecha_registro = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
