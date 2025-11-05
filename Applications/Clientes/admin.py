from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'tipo_cliente', 'fecha_registro', 'activo')
    search_fields = ('nombre', 'apellido', 'correo')
    list_filter = ('tipo_cliente', 'activo')