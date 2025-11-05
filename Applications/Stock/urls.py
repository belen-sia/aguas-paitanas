from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('actualizar/<int:producto_id>/', views.actualizar_stock, name='actualizar_stock'),
    path('actualizar-form/<int:producto_id>/', views.actualizar_stock_form, name='actualizar_stock_form'),
]

