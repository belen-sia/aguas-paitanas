from django.contrib import admin
from .models import Sucursal

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion')
