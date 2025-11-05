from django.urls import path
from . import views

app_name = 'mermas'

urlpatterns = [
    path('registrar/<int:producto_id>/', views.registrar_merma, name='registrar_merma'),
]
