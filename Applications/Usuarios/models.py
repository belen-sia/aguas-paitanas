from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

# -----------------------
# Cliente
# -----------------------
class Cliente(models.Model):
    TIPO_CLIENTE = [
        ('D', 'Domiciliario'),
        ('E', 'Empresa'),
    ]

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)  # +569XXXXXXXX
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


# -----------------------
# Usuario (trabajador/repartidor/administrador)
# -----------------------
class UsuarioManager(BaseUserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, True, True, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('TRAB', 'Trabajador'),
        ('REPAR', 'Repartidor')
    ]
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    rol = models.CharField(max_length=5, choices=ROLES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

