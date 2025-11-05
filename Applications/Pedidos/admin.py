from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1  # Muestra al menos un campo vacío para agregar detalle
    readonly_fields = ('subtotal',)  # El subtotal se calcula automáticamente


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'repartidor', 'fecha_pedido', 'estado', 'monto_total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__nombre', 'repartidor__nombre')
    inlines = [DetallePedidoInline]

    fieldsets = (
        ('Información del pedido', {
            'fields': ('cliente', 'repartidor', 'estado', 'observaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_entrega')
        }),
        ('Totales', {
            'fields': ('monto_total',)
        }),
    )

    readonly_fields = ('fecha_pedido', 'monto_total')  # No editables


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('pedido__id', 'producto__nombre')

from Applications.Pagos.models import MetodoPago, TipoFacturacion, Pago

# Registrar Métodos de Pago
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_pago')
    search_fields = ('tipo_pago',)

# Registrar Tipo de Facturación
@admin.register(TipoFacturacion)
class TipoFacturacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'tipo_documento', 'numero_documento', 'fecha_emision', 'total')
    search_fields = ('tipo_documento', 'numero_documento')

# Registrar Pagos
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'metodo_pago', 'monto', 'estado', 'fecha')
    list_filter = ('estado', 'metodo_pago')
    search_fields = ('pedido__id',)
