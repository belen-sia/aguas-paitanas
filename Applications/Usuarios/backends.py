# Usuarios/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import Usuario
from Applications.Clientes.models import Cliente

class EmailBackend(ModelBackend):
    """
    Autenticación usando el email como username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(email=username)
            if user.check_password(password):
                return user
        except Usuario.DoesNotExist:
            return None

class ClienteBackend(ModelBackend):
    """
    Autenticación de Clientes usando el correo como username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            cliente = Cliente.objects.get(correo=username)
            if cliente.check_password(password):
                return cliente
        except Cliente.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Cliente.objects.get(pk=user_id)
        except Cliente.DoesNotExist:
            return None
