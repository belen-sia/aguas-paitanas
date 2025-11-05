from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Applications.Mermas.models import Merma
from Applications.Productos.models import Producto
from Applications.Sucursales.models import Sucursal
from django.utils import timezone

def registrar_merma(request, producto_id):
    # Obtener producto y sucursales
    producto = get_object_or_404(Producto, id=producto_id)
    sucursales = Sucursal.objects.all()
    historial_mermas = Merma.objects.filter(producto=producto).order_by('-fecha')

    MIN_STOCK = 10

    if request.method == 'POST':
        try:
            sucursal = get_object_or_404(Sucursal, id=request.POST.get('sucursal_id'))
            cantidad = int(request.POST.get('cantidad'))
            motivo = request.POST.get('motivo')
            costo = float(request.POST.get('costo'))

            # Fecha opcional
            fecha_str = request.POST.get('fecha')
            fecha = fecha_str if fecha_str else timezone.now().date()

            # Validar stock
            if cantidad > producto.stock:
                messages.error(
                    request,
                    f'❌ No hay suficiente stock para registrar esta merma. Stock actual: {producto.stock} unidades.'
                )
                return redirect('mermas:registrar_merma', producto_id=producto.id)

            # Registrar la merma
            Merma.objects.create(
                producto=producto,
                sucursal=sucursal,
                cantidad=cantidad,
                motivo=motivo,
                costo=costo,
                fecha=fecha
            )

            # Descontar del stock
            producto.stock -= cantidad
            producto.save()

            # Alerta por stock bajo tras registrar merma
            try:
                if request.user.is_authenticated and getattr(request.user, 'rol', None) in ('ADMIN', 'TRAB') and producto.stock <= MIN_STOCK:
                    messages.warning(request, f"⚠️ El stock de {producto.nombre} es {producto.stock} (≤ {MIN_STOCK}). Reponer stock.")
            except Exception:
                pass

            messages.success(
                request,
                f'✅ Merma registrada correctamente para {producto.nombre}. Se descontaron {cantidad} unidades del stock.'
            )
            return redirect('mermas:registrar_merma', producto_id=producto.id)

        except Exception as e:
            messages.error(request, f'❌ Error al registrar merma: {e}')
            return redirect('mermas:registrar_merma', producto_id=producto.id)

    # GET: mostrar formulario con historial con alerta si stock bajo
    try:
        if request.user.is_authenticated and getattr(request.user, 'rol', None) in ('ADMIN', 'TRAB') and producto.stock <= MIN_STOCK:
            messages.warning(request, f"⚠️ El stock de {producto.nombre} es {producto.stock} (≤ {MIN_STOCK}). Reponer stock.")
    except Exception:
        pass

    return render(request, 'gestion/registrar_merma.html', {
        'producto': producto,
        'sucursales': sucursales,
        'historial_mermas': historial_mermas,
        'today': timezone.now().date(),
    })

