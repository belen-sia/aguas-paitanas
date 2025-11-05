from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from django.db.models import Q
import re
from django.core.mail import send_mail
from django.conf import settings

from .models import Pedido, DetallePedido
from Applications.Clientes.models import Cliente
from Applications.Repartidores.models import Repartidor, NotificacionRepartidor
from Applications.Productos.models import Producto
from Applications.Pagos.models import MetodoPago, Pago, TipoFacturacion
from Applications.Usuarios.models import Usuario


# --------------------------
# GESTIÓN DE PEDIDOS
# --------------------------
@login_required
def gestion_pedidos(request):
    rol = request.session.get('rol') or getattr(request.user, 'rol', None)
    if not (rol in ('ADMIN', 'TRAB') or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No autorizado')
        return redirect('redirigir_por_rol')

    pedidos = Pedido.objects.all()

    # Asegurar que haya registros en Repartidor para cada Usuario con rol REPAR
    usuarios_repar = Usuario.objects.filter(rol='REPAR', is_active=True)
    for u in usuarios_repar:
        if u.email:
            rep = Repartidor.objects.filter(correo_electronico__iexact=u.email).first()
            if not rep:
                Repartidor.objects.create(
                    nombre=u.first_name or u.username,
                    apellido=u.last_name or '',
                    telefono='',
                    correo_electronico=u.email,
                    contrasena=''
                )

    repartidores = Repartidor.objects.all()
    ESTADOS = Pedido.ESTADOS

    q = request.GET.get('q', '')
    if q:
        pedidos = pedidos.filter(
            Q(cliente__nombre__icontains=q) |
            Q(cliente__apellido__icontains=q) |
            Q(nombre_cliente_temp__icontains=q) |
            Q(apellido_cliente_temp__icontains=q) |
            Q(estado__icontains=q)
        )

    estado = request.GET.get('estado', '')
    if estado:
        pedidos = pedidos.filter(estado=estado)

    repartidor_asignado = request.GET.get('repartidor_asignado', '')
    if repartidor_asignado == 'si':
        pedidos = pedidos.filter(repartidor__isnull=False)
    elif repartidor_asignado == 'no':
        pedidos = pedidos.filter(repartidor__isnull=True)

    return render(request, 'gestion/gestion_pedidos.html', {
        'pedidos': pedidos,
        'repartidores': repartidores,
        'ESTADOS': ESTADOS
    })


# --------------------------
# CREAR PEDIDO
# --------------------------
def crear_pedido(request):
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    metodos_pago = MetodoPago.objects.all()

    # Diccionarios para tipos de cliente y tipo de factura
    tipos_cliente = dict(Cliente.TIPO_CLIENTE)
    tipos_factura = dict([
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('GUIA', 'Guia')
    ])

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        tipo_cliente = request.POST.get('tipo_cliente')
        tipo_factura = request.POST.get('tipo_factura')
        metodo_pago_id = request.POST.get('metodo_pago')

        if not cliente_id and not nombre:
            messages.error(request, "Debes seleccionar un cliente o ingresar un nombre para pedido rápido.")
            return redirect('pedidos:crear_pedido')

        # Validaciones de cliente rápido (si no hay cliente existente)
        if not cliente_id:
            if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+", nombre or ""):
                messages.error(request, "El nombre (rápido) solo puede contener letras.")
                return redirect('pedidos:crear_pedido')
            if apellido and not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+", apellido):
                messages.error(request, "El apellido (rápido) solo puede contener letras.")
                return redirect('pedidos:crear_pedido')
            if not re.fullmatch(r"\+569\d{8}", telefono or ""):
                messages.error(request, "El teléfono (rápido) debe empezar con +569 y tener 8 dígitos adicionales.")
                return redirect('pedidos:crear_pedido')
            if not tipo_cliente:
                messages.error(request, "Debes seleccionar el tipo de cliente para pedido rápido.")
                return redirect('pedidos:crear_pedido')

        productos_a_pedir = []
        for producto in productos:
            cantidad = request.POST.get(f'cantidad_{producto.id}')
            if cantidad and cantidad.isdigit() and int(cantidad) > 0:
                cantidad = int(cantidad)
                if producto.stock < cantidad:
                    messages.error(
                        request,
                        f"No hay stock suficiente para {producto.nombre}. Disponible: {producto.stock}, solicitado: {cantidad}."
                    )
                    return redirect('pedidos:crear_pedido')
                productos_a_pedir.append((producto, cantidad))

        # CREAR PEDIDO
        if cliente_id:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            # Guardar snapshot de datos del cliente
            pedido = Pedido.objects.create(
                cliente=cliente,
                nombre_cliente_temp=cliente.nombre,
                apellido_cliente_temp=cliente.apellido,
                direccion_temp=cliente.direccion,
                telefono_temp=cliente.telefono,
                tipo_cliente=None
            )
        else:
            # Pedido rápido (sin cliente registrado)
            pedido = Pedido.objects.create(
                cliente=None,
                nombre_cliente_temp=nombre,
                apellido_cliente_temp=apellido,
                direccion_temp=direccion,
                telefono_temp=telefono,
                tipo_cliente=tipo_cliente
            )

        # Crear detalles y actualizar stock
        for producto, cantidad in productos_a_pedir:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            producto.stock -= cantidad
            producto.save(update_fields=['stock'])

        # Calcular total del pedido
        total_pedido = sum([d.subtotal for d in pedido.detalles.all()])

        # Crear tipo de facturación
        if tipo_factura:
            from Applications.Pagos.models import TipoFacturacion
            # Generar número de documento simple: PED+id+fecha
            numero_doc = f"PED{pedido.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            facturacion = TipoFacturacion.objects.create(
                pedido=pedido,
                tipo_documento=tipo_factura,
                numero_documento=numero_doc,
                total=total_pedido
            )
        else:
            facturacion = None

        # Crear pago asociado
        if metodo_pago_id:
            metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id)
            Pago.objects.create(
                pedido=pedido,
                metodo_pago=metodo_pago,
                facturacion=facturacion,
                monto=total_pedido,
                estado='PENDIENTE'
            )

        # Enviar correo al cliente si el pedido fue creado para un cliente existente con correo
        try:
            if getattr(pedido, 'cliente', None) and getattr(pedido.cliente, 'correo', None):
                cliente = pedido.cliente
                subject = "¡Pedido realizado con éxito!"
                nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()

                # Construcción de resumen (texto)
                summary_lines = []
                detalles = pedido.detalles.select_related('producto')
                for d in detalles:
                    producto_nombre = getattr(d.producto, 'nombre', 'Producto')
                    precio = getattr(d, 'precio_unitario', 0)
                    cantidad = getattr(d, 'cantidad', 0)
                    subtotal_linea = getattr(d, 'subtotal', None)
                    if subtotal_linea is None:
                        subtotal_linea = precio * cantidad
                    summary_lines.append(
                        f"- {producto_nombre}: {cantidad} x ${precio:.2f} = ${subtotal_linea:.2f}"
                    )
                resumen_texto = "\n".join(summary_lines)

                message = (
                    f"¡Hola {nombre_cliente}! \U0001F499\n"
                    f"Tu pedido #{pedido.id} ha sido registrado con éxito en nuestro sistema.\n"
                    f"Nuestro equipo comenzará a preparar tu pedido y te informaremos cuando se encuentre en proceso.\n"
                    f"Te notificaremos vía telefónica ante cualquier inconveniente o actualización sobre tu pedido.\n\n"
                    f"Resumen del pedido:\n{resumen_texto}\n"
                    f"Total: ${total_pedido:.2f}\n\n"
                    f"Gracias por confiar en Aguas Paitanás y preferir la pureza que nos caracteriza.\n"
                    f"Estamos felices de poder atenderte y llevarte agua de calidad directamente a tu hogar.\n"
                    f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                    f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                    f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                )

                # Construcción de resumen (HTML)
                rows_html = "".join([
                    f"<tr>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;'>{getattr(d.producto,'nombre','Producto')}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:center;'>{getattr(d,'cantidad',0)}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right;'>${getattr(d,'precio_unitario',0):.2f}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right;'>${(getattr(d,'subtotal',None) if getattr(d,'subtotal',None) is not None else getattr(d,'precio_unitario',0)*getattr(d,'cantidad',0)):.2f}</td>"
                    f"</tr>" for d in detalles
                ])

                html_message = f"""
                <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                  <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>💙</span></h2>
                  <p>Tu pedido <strong>#{pedido.id}</strong> ha sido <strong>registrado con éxito</strong> en nuestro sistema.</p>
                  <p>Nuestro equipo comenzará a preparar tu pedido y te informaremos cuando se encuentre en proceso.</p>
                  <p>Te notificaremos vía telefónica ante cualquier inconveniente o actualización sobre tu pedido.</p>

                  <h3 style='margin:16px 0 8px;'>Resumen del pedido</h3>
                  <table role='presentation' cellpadding='0' cellspacing='0' width='100%' style='border-collapse:collapse;font-size:14px;'>
                    <thead>
                      <tr>
                        <th align='left' style='padding:8px;border-bottom:2px solid #e5e7eb;'>Producto</th>
                        <th align='center' style='padding:8px;border-bottom:2px solid #e5e7eb;'>Cant.</th>
                        <th align='right' style='padding:8px;border-bottom:2px solid #e5e7eb;'>Precio</th>
                        <th align='right' style='padding:8px;border-bottom:2px solid #e5e7eb;'>Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows_html}
                      <tr>
                        <td colspan='3' style='padding:10px 8px; text-align:right; font-weight:bold;'>Total</td>
                        <td style='padding:10px 8px; text-align:right; font-weight:bold;'>${total_pedido:.2f}</td>
                      </tr>
                    </tbody>
                  </table>

                  <p style='margin:16px 0;'><strong>💧 Aguas Paitanás — pureza que te acompaña siempre.</strong></p>
                  <p style='color:#6b7280; font-size:12px; margin-top:8px;'>⚠️ Por favor, no respondas a este correo. Este mensaje fue enviado automáticamente por Aguas Paitanás.</p>

                  <hr style='border:none; border-top:1px solid #e5e7eb; margin:20px 0;'>

                  <div style='background:#E6F4FF; border:1px solid #bfdbfe; padding:12px; border-radius:8px;'>
                    <table role='presentation' cellpadding='0' cellspacing='0' width='100%' style='font-size:14px;'>
                      <tr>
                        <td style='vertical-align:top; padding:8px 0;'>
                          <h3 style='margin:0 0 8px;'>Contacto</h3>
                          <p style='margin:4px 0;'><strong>Dirección:</strong> Carmen 1247, Vallenar, Atacama, Chile</p>
                          <p style='margin:4px 0;'><strong>Teléfonos:</strong> +56 9 8264 6824 / +56 9 5698 7966 / +56 51 2612529</p>
                          <p style='margin:4px 0;'><strong>Email:</strong> aguapurificadapaitanas@gmail.com</p>
                          <p style='margin:4px 0;'><strong>Horario:</strong> Lunes a Viernes de 9:00 a 18:00 hrs. Sábado de 9:00 a 13:00 hrs</p>
                          <p style='margin:8px 0;'>
                            <a href='https://web.facebook.com/p/Aguas-Filtradas-Paitan%C3%A1s-61567994830670/?_rdc=1&_rdr#' style='color:#2563eb; text-decoration:none;'>Facebook</a> ·
                            <a href='https://www.instagram.com/aguapaitanas/?igsh=M3NvaDRqMDFpNXlx&utm_source=qr#' style='color:#2563eb; text-decoration:none;'>Instagram</a> ·
                            <a href='https://wa.me/56982646824' style='color:#2563eb; text-decoration:none;'>WhatsApp</a>
                          </p>
                        </td>
                      </tr>
                    </table>
                  </div>
                </div>
                """

                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost')
                send_mail(subject, message, from_email, [cliente.correo], fail_silently=False, html_message=html_message)
        except Exception:
            # No interrumpe el flujo si falla el correo
            pass

        messages.success(request, f"Pedido {pedido.id} creado correctamente.")
        return redirect('pedidos:gestion_pedidos')

    return render(request, 'gestion/crear_pedido.html', {
        'clientes': clientes,
        'productos': productos,
        'metodos_pago': metodos_pago,
        'tipos_cliente': tipos_cliente,
        'tipos_factura': tipos_factura
    })


# --------------------------
# DETALLE DE PEDIDO
# --------------------------
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()
    return render(request, 'gestion/detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles
    })


# --------------------------
# ACTUALIZAR ESTADO
# --------------------------
def actualizar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Autorización: ADMIN/SUPERUSER siempre; REPAR solo para estados permitidos y si el pedido está asignado a él
    rol = request.session.get('rol') or getattr(request.user, 'rol', None)
    es_admin = (rol == 'ADMIN' or getattr(request.user, 'is_superuser', False))

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = dict(Pedido.ESTADOS)
        if nuevo_estado in estados_validos:
            autorizado = False
            if es_admin:
                autorizado = True
            elif rol == 'REPAR':
                # Solo puede alternar entre PENDIENTE/EN_PROCESO/ENTREGADO y solo si está asignado
                permitidos_repar = {'PENDIENTE', 'EN_PROCESO', 'ENTREGADO'}
                rep = getattr(pedido, 'repartidor', None)
                correo_user = getattr(request.user, 'email', None)
                if rep and correo_user and rep.correo_electronico and rep.correo_electronico.lower() == correo_user.lower() and nuevo_estado in permitidos_repar:
                    autorizado = True
            if not autorizado:
                messages.error(request, 'No autorizado para cambiar este estado del pedido.')
                return redirect('pedidos:gestion_pedidos')

            # Aplicar cambio de estado
            if nuevo_estado == 'ENTREGADO' and pedido.fecha_entrega is None:
                pedido.fecha_entrega = date.today()
            elif nuevo_estado != 'ENTREGADO':
                pedido.fecha_entrega = None
            pedido.estado = nuevo_estado
            pedido.save(update_fields=['estado', 'fecha_entrega'])

            # Enviar correo al cliente según nuevo estado
            if getattr(pedido, 'cliente', None) and getattr(pedido.cliente, 'correo', None):
                try:
                    cliente = pedido.cliente
                    nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()

                    subject = None
                    message = None
                    html_message = None

                    if nuevo_estado == 'EN_PROCESO':
                        subject = f"Tu pedido #{pedido.id} está en proceso"
                        message = (
                            f"¡Hola {nombre_cliente}! \U0001F30A\U0001F4A7\n"
                            f"Queremos informarte que tu pedido #{pedido.id} ahora se encuentra en proceso.\n"
                            f"Nuestro equipo está preparando tu pedido con dedicación para que pronto puedas disfrutar de nuestros productos.\n"
                            f"Te notificaremos vía telefónica ante cualquier inconveniente o cuando tu entrega esté lista para despacho.\n"
                            f"Gracias por confiar en Aguas Paitanás y permitirnos ser parte de tu día a día.\n"
                            f"\U0001F499 Aguas Paitanás — pureza que te acompaña siempre.\n"
                            f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                            f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                        )
                        html_message = f"""
                        <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                          <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>🌊💧</span></h2>
                          <p>Queremos informarte que tu pedido <strong>#{pedido.id}</strong> ahora se encuentra <strong>en proceso</strong>.</p>
                          <p>Nuestro equipo está preparando tu pedido con dedicación para que pronto puedas disfrutar de nuestros productos.</p>
                          <p>Te notificaremos vía telefónica ante cualquier inconveniente o cuando tu entrega esté lista para despacho.</p>
                          <p>Gracias por confiar en <strong>Aguas Paitanás</strong> y permitirnos ser parte de tu día a día.</p>
                          <p style='margin:16px 0;'><strong>💙 Aguas Paitanás — pureza que te acompaña siempre.</strong></p>
                          <p style='color:#6b7280; font-size:12px; margin-top:8px;'>⚠️ Por favor, no respondas a este correo. Este mensaje fue enviado automáticamente por Aguas Paitanás.</p>

                          <hr style='border:none; border-top:1px solid #e5e7eb; margin:20px 0;'>

                          <div style='background:#E6F4FF; border:1px solid #bfdbfe; padding:12px; border-radius:8px;'>
                            <table role='presentation' cellpadding='0' cellspacing='0' width='100%' style='font-size:14px;'>
                              <tr>
                                <td style='vertical-align:top; padding:8px 0;'>
                                  <h3 style='margin:0 0 8px;'>Contacto</h3>
                                  <p style='margin:4px 0;'><strong>Dirección:</strong> Carmen 1247, Vallenar, Atacama, Chile</p>
                                  <p style='margin:4px 0;'><strong>Teléfonos:</strong> +56 9 8264 6824 / +56 9 5698 7966 / +56 51 2612529</p>
                                  <p style='margin:4px 0;'><strong>Email:</strong> aguapurificadapaitanas@gmail.com</p>
                                  <p style='margin:4px 0;'><strong>Horario:</strong> Lunes a Viernes de 9:00 a 18:00 hrs. Sábado de 9:00 a 13:00 hrs</p>
                                  <p style='margin:8px 0;'>
                                    <a href='https://web.facebook.com/p/Aguas-Filtradas-Paitan%C3%A1s-61567994830670/?_rdc=1&_rdr#' style='color:#2563eb; text-decoration:none;'>Facebook</a> ·
                                    <a href='https://www.instagram.com/aguapaitanas/?igsh=M3NvaDRqMDFpNXlx&utm_source=qr#' style='color:#2563eb; text-decoration:none;'>Instagram</a> ·
                                    <a href='https://wa.me/56982646824' style='color:#2563eb; text-decoration:none;'>WhatsApp</a>
                                  </p>
                                </td>
                              </tr>
                            </table>
                          </div>
                        </div>
                        """
                    elif nuevo_estado == 'ENTREGADO':
                        subject = f"Tu pedido #{pedido.id} ha sido entregado"
                        message = (
                            f"¡Hola {nombre_cliente}! \U0001F499\n"
                            f"Nos complace informarte que tu pedido #{pedido.id} ha sido entregado exitosamente.\n"
                            f"Esperamos que disfrutes de nuestros productos y que siempre tengas agua de calidad a tu disposición.\n"
                            f"Gracias por confiar en Aguas Paitanás y permitirnos acompañarte en tu día a día.\n"
                            f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                            f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                            f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                        )
                        html_message = f"""
                        <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                          <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>💙</span></h2>
                          <p>Nos complace informarte que tu pedido <strong>#{pedido.id}</strong> ha sido <strong>entregado exitosamente</strong>.</p>
                          <p>Esperamos que disfrutes de nuestros productos y que siempre tengas agua de calidad a tu disposición.</p>
                          <p>Gracias por confiar en <strong>Aguas Paitanás</strong> y permitirnos acompañarte en tu día a día.</p>
                          <p style='margin:16px 0;'><strong>💧 Aguas Paitanás — pureza que te acompaña siempre.</strong></p>
                          <p style='color:#6b7280; font-size:12px; margin-top:8px;'>⚠️ Por favor, no respondas a este correo. Este mensaje fue enviado automáticamente por Aguas Paitanás.</p>

                          <hr style='border:none; border-top:1px solid #e5e7eb; margin:20px 0;'>

                          <div style='background:#E6F4FF; border:1px solid #bfdbfe; padding:12px; border-radius:8px;'>
                            <table role='presentation' cellpadding='0' cellspacing='0' width='100%' style='font-size:14px;'>
                              <tr>
                                <td style='vertical-align:top; padding:8px 0;'>
                                  <h3 style='margin:0 0 8px;'>Contacto</h3>
                                  <p style='margin:4px 0;'><strong>Dirección:</strong> Carmen 1247, Vallenar, Atacama, Chile</p>
                                  <p style='margin:4px 0;'><strong>Teléfonos:</strong> +56 9 8264 6824 / +56 9 5698 7966 / +56 51 2612529</p>
                                  <p style='margin:4px 0;'><strong>Email:</strong> aguapurificadapaitanas@gmail.com</p>
                                  <p style='margin:4px 0;'><strong>Horario:</strong> Lunes a Viernes de 9:00 a 18:00 hrs. Sábado de 9:00 a 13:00 hrs</p>
                                  <p style='margin:8px 0;'>
                                    <a href='https://web.facebook.com/p/Aguas-Filtradas-Paitan%C3%A1s-61567994830670/?_rdc=1&_rdr#' style='color:#2563eb; text-decoration:none;'>Facebook</a> ·
                                    <a href='https://www.instagram.com/aguapaitanas/?igsh=M3NvaDRqMDFpNXlx&utm_source=qr#' style='color:#2563eb; text-decoration:none;'>Instagram</a> ·
                                    <a href='https://wa.me/56982646824' style='color:#2563eb; text-decoration:none;'>WhatsApp</a>
                                  </p>
                                </td>
                              </tr>
                            </table>
                          </div>
                        </div>
                        """
                    elif nuevo_estado == 'CANCELADO':
                        subject = f"Tu pedido #{pedido.id} ha sido cancelado"
                        message = (
                            f"¡Hola {nombre_cliente}! \U0001F499\n"
                            f"Lamentamos informarte que tu pedido #{pedido.id} ha sido cancelado.\n"
                            f"Si fue un error o necesitas realizar un nuevo pedido, no dudes en volver a nuestra plataforma para gestionarlo.\n\n"
                            f"Gracias por confiar en Aguas Paitanás y esperamos poder atenderte nuevamente pronto.\n"
                            f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                            f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                            f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                        )
                        html_message = f"""
                        <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                          <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>💙</span></h2>
                          <p>Lamentamos informarte que tu pedido <strong>#{pedido.id}</strong> ha sido <strong>cancelado</strong>.</p>
                          <p>Si fue un error o necesitas realizar un nuevo pedido, no dudes en volver a nuestra plataforma para gestionarlo.</p>
                          <p>Gracias por confiar en <strong>Aguas Paitanás</strong> y esperamos poder atenderte nuevamente pronto.</p>
                          <p style='margin:16px 0;'><strong>💧 Aguas Paitanás — pureza que te acompaña siempre.</strong></p>
                          <p style='color:#6b7280; font-size:12px; margin-top:8px;'>⚠️ Por favor, no respondas a este correo. Este mensaje fue enviado automáticamente por Aguas Paitanás.</p>

                          <hr style='border:none; border-top:1px solid #e5e7eb; margin:20px 0;'>

                          <div style='background:#E6F4FF; border:1px solid #bfdbfe; padding:12px; border-radius:8px;'>
                            <table role='presentation' cellpadding='0' cellspacing='0' width='100%' style='font-size:14px;'>
                              <tr>
                                <td style='vertical-align:top; padding:8px 0;'>
                                  <h3 style='margin:0 0 8px;'>Contacto</h3>
                                  <p style='margin:4px 0;'><strong>Dirección:</strong> Carmen 1247, Vallenar, Atacama, Chile</p>
                                  <p style='margin:4px 0;'><strong>Teléfonos:</strong> +56 9 8264 6824 / +56 9 5698 7966 / +56 51 2612529</p>
                                  <p style='margin:4px 0;'><strong>Email:</strong> aguapurificadapaitanas@gmail.com</p>
                                  <p style='margin:4px 0;'><strong>Horario:</strong> Lunes a Viernes de 9:00 a 18:00 hrs. Sábado de 9:00 a 13:00 hrs</p>
                                  <p style='margin:8px 0;'>
                                    <a href='https://web.facebook.com/p/Aguas-Filtradas-Paitan%C3%A1s-61567994830670/?_rdc=1&_rdr#' style='color:#2563eb; text-decoration:none;'>Facebook</a> ·
                                    <a href='https://www.instagram.com/aguapaitanas/?igsh=M3NvaDRqMDFpNXlx&utm_source=qr#' style='color:#2563eb; text-decoration:none;'>Instagram</a> ·
                                    <a href='https://wa.me/56982646824' style='color:#2563eb; text-decoration:none;'>WhatsApp</a>
                                  </p>
                                </td>
                              </tr>
                            </table>
                          </div>
                        </div>
                        """

                    if subject and message and html_message:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost')
                        send_mail(subject, message, from_email, [cliente.correo], fail_silently=False, html_message=html_message)
                except Exception:
                    # No interrumpe la actualización del pedido si el correo falla
                    pass

            # Notificar al repartidor si el pedido tiene uno asignado
            rep = getattr(pedido, 'repartidor', None)
            rep_mail = getattr(rep, 'correo_electronico', None)
            if rep_mail:
                try:
                    NotificacionRepartidor.objects.create(
                        correo_electronico=rep_mail,
                        pedido_id=pedido.id,
                        mensaje=f"El pedido #{pedido.id} cambió su estado a {pedido.get_estado_display()}."
                    )
                except Exception:
                    pass

            messages.success(
                request,
                f"El pedido #{pedido.id} fue actualizado a {pedido.get_estado_display()} correctamente."
            )

    return redirect('pedidos:gestion_pedidos')


# --------------------------
# ASIGNAR REPARTIDOR (solo admin)
# --------------------------
@staff_member_required
def asignar_repartidor(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        repartidor_id = request.POST.get('repartidor_id')
        if repartidor_id:
            repartidor = get_object_or_404(Repartidor, id=repartidor_id)
            pedido.repartidor = repartidor
            pedido.save()

            # Notificación para el repartidor asignado
            try:
                NotificacionRepartidor.objects.create(
                    correo_electronico=repartidor.correo_electronico,
                    pedido_id=pedido.id,
                    mensaje=f"Se te asignó el pedido #{pedido.id}."
                )
            except Exception:
                pass

            messages.success(request, f"Repartidor {repartidor.nombre} asignado al pedido {pedido.id}.")
        else:
            pedido.repartidor = None
            pedido.save()
            messages.info(request, f"Repartidor desasignado del pedido {pedido.id}.")
    return redirect('pedidos:gestion_pedidos')


# --------------------------
# ELIMINAR PEDIDO
# --------------------------
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, f"Pedido {pedido.id} eliminado correctamente.")
    return redirect('pedidos:gestion_pedidos')