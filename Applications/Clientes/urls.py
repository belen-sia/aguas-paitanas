from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('portalclientes/', views.portalclientes, name='portalclientes'),
    path('perfil/', views.editar_perfil_cliente, name='editar_perfil'),
    path('eliminar-cuenta/', views.eliminar_cuenta_cliente, name='eliminar_cuenta'),
    path('carrito/', views.carrito, name='carrito'),
    path('gestion/', views.gestion_clientes, name='gestion_clientes'),
    path('editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
]
