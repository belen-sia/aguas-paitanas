"""
URL configuration for AguasPaitanas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('home.urls', namespace='home')),
    path('clientes/', include('Applications.Clientes.urls')),
    path('trabajadores/', include('Applications.Trabajadores.urls')),
    path('productos/', include('Applications.Productos.urls')),
    path('pedidos/', include('Applications.Pedidos.urls')),
    path('usuarios/', include('Applications.Usuarios.urls')),
    path('stock/', include('Applications.Stock.urls')),
    path('mermas/', include('Applications.Mermas.urls')),
    path('repartidores/', include('Applications.Repartidores.urls')),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else [])
