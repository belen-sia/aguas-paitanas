from django.urls import path
from .views import InicioIndexView, RegistrarView, ContactoView, CerrarsesionView

app_name = 'home'

urlpatterns = [
    path('', InicioIndexView.as_view(), name='inicioindex'),
    path('registrar/', RegistrarView.as_view(), name='registrar'),
    path('contacto/', ContactoView.as_view(), name='contacto'),
    path('cerrarsesion/', CerrarsesionView.as_view(), name='cerrarsesion'),
]

