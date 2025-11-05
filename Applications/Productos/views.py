from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Applications.Productos.models import Producto
from Applications.Sucursales.models import Sucursal
from Applications.Stock.models import Stock
from Applications.Mermas.models import Merma

# Vista para gestionar productos con búsqueda
def gestion_productos(request):
    query = request.GET.get('q', '')  # Obtenemos el término de búsqueda
    productos = Producto.objects.all()
    if query:
        productos = productos.filter(nombre__icontains=query)  # Filtramos por nombre

    # Alerta para ADMIN o TRAB si hay productos con stock bajo o igual a 10
    try:
        if request.user.is_authenticated and getattr(request.user, 'rol', None) in ('ADMIN', 'TRAB'):
            bajos = productos.filter(stock__lte=10)
            if bajos.exists():
                total_bajos = bajos.count()
                messages.warning(
                    request,
                    f"⚠️ Hay {total_bajos} producto(s) con stock inferior o igual a 10. Se solicita reponer stock."
                )
    except Exception:
        pass

    sucursales = Sucursal.objects.all()
    return render(request, 'gestion/gestion_productos.html', {
        'productos': productos,
        'sucursales': sucursales,
        'query': query  # Para mantener el valor en el input
    })


# Vista para crear un nuevo producto
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        volumen = request.POST.get('volumen')
        precio = int(request.POST.get('precio'))
        descripcion = request.POST.get('descripcion', '')

        Producto.objects.create(
            nombre=nombre,
            categoria=categoria,
            volumen=volumen,
            precio=precio,
            descripcion=descripcion
        )
        messages.success(request, f'Producto "{nombre}" creado correctamente.')
        return redirect('productos:gestion_productos')

    categorias = Producto.CATEGORIAS
    volumenes = Producto.VOLUMENES
    return render(request, 'gestion/crear_producto.html', {
        'categorias': categorias,
        'volumenes': volumenes
    })


# Vista para actualizar stock con tipo de movimiento
def actualizar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('nueva_cantidad'))
            sucursal_id = request.POST.get('sucursal_id')
            tipo_movimiento = request.POST.get('tipo_movimiento', 'AJUSTE')
            sucursal = get_object_or_404(Sucursal, id=sucursal_id)

            stock_obj, created = Stock.objects.get_or_create(
                producto=producto,
                sucursal=sucursal,
                defaults={'cantidad_actual': nueva_cantidad, 'tipo_movimiento': tipo_movimiento}
            )

            if not created:
                if tipo_movimiento == "ENTRADA":
                    stock_obj.cantidad_actual += nueva_cantidad
                elif tipo_movimiento == "SALIDA":
                    stock_obj.cantidad_actual -= nueva_cantidad
                    if stock_obj.cantidad_actual < 0:
                        stock_obj.cantidad_actual = 0
                elif tipo_movimiento == "AJUSTE":
                    stock_obj.cantidad_actual = nueva_cantidad
                stock_obj.tipo_movimiento = tipo_movimiento
                stock_obj.save()

            # Actualizamos stock total del producto
            total_stock = sum(s.cantidad_actual for s in producto.stocks.all())
            producto.stock = total_stock
            producto.save()

            messages.success(request, f'Stock actualizado correctamente para {producto.nombre}.')
        except Exception as e:
            messages.error(request, f'Error al actualizar stock: {e}')

    return redirect('productos:gestion_productos')


# Vista para registrar merma
def registrar_merma(request):
    if request.method == 'POST':
        try:
            producto_id = request.POST.get('producto_id')
            sucursal_id = request.POST.get('sucursal_id')
            cantidad = int(request.POST.get('cantidad'))
            tipo_merma = request.POST.get('tipo_merma', '')  # Si tienes tipos de merma
            costo = float(request.POST.get('costo'))
            motivo = request.POST.get('motivo', '')

            producto = get_object_or_404(Producto, id=producto_id)
            sucursal = get_object_or_404(Sucursal, id=sucursal_id)

            Merma.objects.create(
                producto=producto,
                sucursal=sucursal,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                costo=costo,
                motivo=motivo
                # fecha se completa automáticamente si usas auto_now_add
            )

            messages.success(request, f'Merma registrada correctamente para {producto.nombre}.')
        except Exception as e:
            messages.error(request, f'Error al registrar merma: {e}')

    return redirect('productos:gestion_productos')

# Vista para eliminar un producto
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        producto.delete()
        messages.success(request, f'Producto "{producto.nombre}" eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar producto: {e}')
    return redirect('productos:gestion_productos')





