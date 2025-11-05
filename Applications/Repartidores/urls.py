from django.urls import path
from . import views

app_name = 'repartidores'

urlpatterns = [
    path('portalrepartidores/', views.portalrepartidores, name='portalrepartidores'),
    path('pedidos_asignados/', views.pedidos_asignados, name='pedidos_asignados'),
    path('historial_entregas/', views.historial_entregas, name='historial_entregas'),
    path('actualizar_pedido/<int:pedido_id>/', views.actualizar_estado_repartidor, name='actualizar_pedido_repartidor'),
]
