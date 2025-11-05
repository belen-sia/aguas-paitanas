from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('gestion_productos/', views.gestion_productos, name='gestion_productos'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),


]




