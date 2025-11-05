from django.urls import path
from . import views

app_name = 'trabajadores'

urlpatterns = [
    path('portaladministrador/', views.portal_administrador, name='portaladministrador'),
    path('portaltrabajadores/', views.portal_trabajadores, name='portaltrabajadores'),
    path('reportes/', views.reportes, name='reportes'),
    path('agregar_trabajador/', views.agregar_trabajador, name='agregar_trabajador'),
    path('reportes/', views.reportes, name='reportes'),
]
