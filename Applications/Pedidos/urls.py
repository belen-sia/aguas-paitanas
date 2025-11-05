from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('gestion_pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('crear_pedido/', views.crear_pedido, name='crear_pedido'),
    path('detalle_pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('actualizar_pedido/<int:pedido_id>/', views.actualizar_pedido, name='actualizar_pedido'),
    path('asignar_repartidor/<int:pedido_id>/', views.asignar_repartidor, name='asignar_repartidor'),
    path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),

]

