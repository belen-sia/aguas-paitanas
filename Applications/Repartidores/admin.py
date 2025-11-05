from django.contrib import admin
from .models import Repartidor

@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono', 'correo_electronico')
    search_fields = ('nombre', 'apellido', 'correo_electronico')
    list_filter = ('apellido',)
