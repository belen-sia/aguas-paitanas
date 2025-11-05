from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Applications.Productos.models import Producto
from Applications.Stock.models import Stock
from Applications.Sucursales.models import Sucursal

def actualizar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('nueva_cantidad'))
            sucursal_id = request.POST.get('sucursal_id')
            tipo_movimiento = request.POST.get('tipo_movimiento')

            sucursal = get_object_or_404(Sucursal, id=sucursal_id)

            # Obtenemos o creamos el stock de esa sucursal
            stock_obj, created = Stock.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,
                defaults={'cantidad_actual': 0, 'tipo_movimiento': 'AJUSTE'}
            )

            if tipo_movimiento == 'ENTRADA':
                stock_obj.cantidad_actual += cantidad
            elif tipo_movimiento == 'SALIDA':
                if cantidad > stock_obj.cantidad_actual:
                    messages.error(request, f"❌ No se puede restar {cantidad}, solo hay {stock_obj.cantidad_actual} en stock.")
                    return redirect('productos:gestion_productos')
                stock_obj.cantidad_actual -= cantidad
            elif tipo_movimiento == 'AJUSTE':
                stock_obj.cantidad_actual = cantidad
            else:
                messages.error(request, "❌ Tipo de movimiento no válido.")
                return redirect('productos:gestion_productos')

            stock_obj.tipo_movimiento = tipo_movimiento
            stock_obj.save()

            # Actualizamos el stock total del producto sumando todas las sucursales
            producto.stock = sum(s.cantidad_actual for s in producto.stocks.all())
            producto.save()

            # Alerta si stock bajo para ADMIN/TRAB
            try:
                if request.user.is_authenticated and getattr(request.user, 'rol', None) in ('ADMIN', 'TRAB') and producto.stock <= 10:
                    messages.warning(request, f"⚠️ El stock de {producto.nombre} es {producto.stock} (≤ 10). Reponer stock.")
            except Exception:
                pass

            messages.success(request, f"✅ Stock actualizado correctamente para {producto.nombre} ({tipo_movimiento}).")
        except Exception as e:
            messages.error(request, f"❌ Error al actualizar stock: {e}")

    return redirect('productos:gestion_productos')

def actualizar_stock_form(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    sucursales = Sucursal.objects.all()
    return render(request, 'gestion/actualizar_stock.html', {
        'producto': producto,
        'sucursales': sucursales
    })
