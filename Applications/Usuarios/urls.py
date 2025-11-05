from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.iniciar_sesion, name='iniciarsesion'),
    path('logout/', views.cerrar_sesion, name='cerrarsesion'),
    path('gestion/', views.gestion_usuarios, name='gestion_usuarios'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
