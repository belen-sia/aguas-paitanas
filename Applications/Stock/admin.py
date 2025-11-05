from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'sucursal', 'cantidad_actual', 'tipo_movimiento', 'fecha_actualizacion')
    list_filter = ('sucursal', 'tipo_movimiento')

