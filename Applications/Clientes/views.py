# Applications/Clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ClienteForm
from .models import Cliente
from django.contrib.auth.hashers import make_password, check_password
from Applications.Productos.models import Producto
from Applications.Pedidos.models import Pedido, DetallePedido
from Applications.Pagos.models import MetodoPago, Pago, TipoFacturacion
from decimal import Decimal
from .decorators import cliente_login_required
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# -------------------------------------------------------------------
# 🔹 Registrar nuevo cliente (autoregistro)
# -------------------------------------------------------------------
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            # Usa el método del modelo para guardar el hash
            cliente.set_password(form.cleaned_data['contrasena'])
            cliente.save()

            # Enviar correo de bienvenida (autoregistro)
            try:
                if getattr(cliente, 'correo', None):
                    subject = "¡Registro completado con éxito! – Bienvenido a Aguas Paitanás"
                    nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()
                    # Texto plano
                    message = (
                        f"¡Hola {nombre_cliente}! \U0001F499\n"
                        f"Tu registro en Aguas Paitanás se ha completado con éxito.\n"
                        f"A partir de ahora podrás realizar tus pedidos de forma rápida y sencilla, además de recibir notificaciones sobre el estado de tus compras.\n"
                        f"Nos alegra que formes parte de nuestra comunidad y esperamos brindarte siempre el mejor servicio.\n"
                        f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                        f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                        f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                    )
                    # HTML
                    html_message = f"""
                    <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                      <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>💙</span></h2>
                      <p>Tu registro en <strong>Aguas Paitanás</strong> se ha completado con éxito.</p>
                      <p>A partir de ahora podrás realizar tus pedidos de forma rápida y sencilla, además de recibir notificaciones sobre el estado de tus compras.</p>
                      <p>Nos alegra que formes parte de nuestra comunidad y esperamos brindarte siempre el mejor servicio.</p>
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
                    send_mail(subject, message, from_email, [cliente.correo], fail_silently=True, html_message=html_message)
            except Exception:
                pass

            messages.success(request, "Cliente registrado correctamente. Ahora puedes iniciar sesión.")
            return redirect('clientes:gestion_clientes')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
            messages.error(request, f"Detalles: {form.errors.as_text()}")
    else:
        form = ClienteForm()

    return render(request, 'home/registrar.html', {'form': form})

# -------------------------------------------------------------------
# 🔹 Registrar cliente desde gestión (no mandar a login)
# -------------------------------------------------------------------
def registrar_cliente_gestion(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()

            # Enviar correo de bienvenida (registro desde gestión)
            try:
                if getattr(cliente, 'correo', None):
                    subject = "¡Registro completado con éxito! – Bienvenido a Aguas Paitanás"
                    nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()
                    message = (
                        f"¡Hola {nombre_cliente}! \U0001F499\n"
                        f"Tu registro en Aguas Paitanás se ha completado con éxito.\n"
                        f"A partir de ahora podrás realizar tus pedidos de forma rápida y sencilla, además de recibir notificaciones sobre el estado de tus compras.\n"
                        f"Nos alegra que formes parte de nuestra comunidad y esperamos brindarte siempre el mejor servicio.\n"
                        f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                        f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                        f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                    )
                    html_message = f"""
                    <div style='font-family:Arial,Helvetica,sans-serif; color:#111827; line-height:1.6;'>
                      <h2 style='margin:0 0 12px;'>¡Hola {nombre_cliente}! <span>💙</span></h2>
                      <p>Tu registro en <strong>Aguas Paitanás</strong> se ha completado con éxito.</p>
                      <p>A partir de ahora podrás realizar tus pedidos de forma rápida y sencilla, además de recibir notificaciones sobre el estado de tus compras.</p>
                      <p>Nos alegra que formes parte de nuestra comunidad y esperamos brindarte siempre el mejor servicio.</p>
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
                pass

            messages.success(request, "Cliente registrado correctamente.")
            return redirect('clientes:gestion_clientes')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
            messages.error(request, f"Detalles: {form.errors.as_text()}")
            return redirect('clientes:gestion_clientes')
    return redirect('clientes:gestion_clientes')

# -------------------------------------------------------------------
# 🔹 Portal Clientes (protegido)
# -------------------------------------------------------------------
@cliente_login_required
def portalclientes(request):
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cliente, id=cliente_id) if cliente_id else None
    return render(request, 'clientes/portalclientes.html', {'cliente': cliente})

# -------------------------------------------------------------------
# 🔹 Perfil del cliente (auto-servicio)
# -------------------------------------------------------------------
@cliente_login_required
def editar_perfil_cliente(request):
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        data = request.POST.copy()
        # Asegurar que tipo_cliente se mantenga aunque no esté en el formulario visible
        data['tipo_cliente'] = cliente.tipo_cliente
        form = ClienteForm(data, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos fueron actualizados correctamente.")
            return redirect('clientes:portalclientes')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
            messages.error(request, f"Detalles: {form.errors.as_text()}")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/editar_perfil.html', { 'form': form, 'cliente': cliente })

# -------------------------------------------------------------------
# 🔹 Eliminar cuenta del cliente (auto-servicio)
# -------------------------------------------------------------------
@cliente_login_required
def eliminar_cuenta_cliente(request):
    if request.method == 'POST':
        cliente_id = request.session.get('cliente_id')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        nombre = f"{cliente.nombre} {cliente.apellido}"
        # Copiar snapshot en pedidos antes de eliminar
        Pedido.objects.filter(cliente=cliente).update(
            nombre_cliente_temp=cliente.nombre,
            apellido_cliente_temp=cliente.apellido,
            direccion_temp=cliente.direccion,
            telefono_temp=cliente.telefono,
        )
        cliente.delete()
        # Limpia la sesión del cliente
        request.session.pop('cliente_id', None)
        request.session.pop('rol', None)
        messages.info(request, f"Cuenta '{nombre}' eliminada correctamente.")
        return redirect('usuarios:iniciarsesion')
    return redirect('clientes:portalclientes')

# -------------------------------------------------------------------
# 🔹 Gestión de clientes
# -------------------------------------------------------------------
def gestion_clientes(request):
    clientes = Cliente.objects.all()
    query = request.GET.get('q')
    if query:
        clientes = clientes.filter(nombre__icontains=query)
    return render(request, 'gestion/gestion_clientes.html', {'clientes': clientes})

# -------------------------------------------------------------------
# 🔹 Editar cliente
# -------------------------------------------------------------------
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        original_tipo = cliente.tipo_cliente
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            # Mantener tipo_cliente inmutable
            cliente.tipo_cliente = original_tipo
            nueva_contrasena = form.cleaned_data.get('contrasena')
            if nueva_contrasena:
                if not (4 <= len(nueva_contrasena) <= 6):
                    messages.error(request, "La contraseña debe tener entre 4 y 6 caracteres.")
                    return redirect('clientes:gestion_clientes')
                cliente.set_password(nueva_contrasena)
            cliente.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect('clientes:gestion_clientes')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos ingresados.")
            return redirect('clientes:gestion_clientes')
    # Si no es POST, redirigir a la gestión (la edición se hace por modal)
    return redirect('clientes:gestion_clientes')

# -------------------------------------------------------------------
# 🔹 Eliminar cliente
# -------------------------------------------------------------------
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        # Copiar snapshot en pedidos antes de eliminar (gestión)
        Pedido.objects.filter(cliente=cliente).update(
            nombre_cliente_temp=cliente.nombre,
            apellido_cliente_temp=cliente.apellido,
            direccion_temp=cliente.direccion,
            telefono_temp=cliente.telefono,
        )
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
        return redirect('clientes:gestion_clientes')
    return render(request, 'gestion/eliminar_cliente.html', {'cliente': cliente})

# -------------------------------------------------------------------
# 🔹 Carrito de compras (protegido)
# -------------------------------------------------------------------
@cliente_login_required
def carrito(request):
    productos = Producto.objects.all()
    cliente_id = request.session.get('cliente_id')
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Cargar opciones de pago y facturación
    metodos_pago = MetodoPago.objects.all()
    tipos_factura = [('BOLETA', 'Boleta'), ('FACTURA', 'Factura'), ('GUIA', 'Guia')]

    if request.method == 'POST':
        # Crear el pedido asociado al cliente registrado
        from Applications.Clientes.models import Cliente as ClienteModel
        tipo_label = dict(ClienteModel.TIPO_CLIENTE).get(cliente.tipo_cliente)

        # Lectura de selecciones de pago/factura
        metodo_pago_id = request.POST.get('metodo_pago_id')
        tipo_factura = request.POST.get('tipo_factura')

        # Validaciones simples de selección
        if not metodo_pago_id or not tipo_factura:
            messages.error(request, 'Debes seleccionar método de pago y tipo de facturación.')
            return redirect('clientes:carrito')

        # Recolectar cantidades solicitadas primero
        seleccion = []
        for producto in productos:
            cantidad_str = request.POST.get(f'producto_{producto.id}')
            if cantidad_str and cantidad_str.isdigit():
                cantidad = int(cantidad_str)
                if cantidad > 0:
                    seleccion.append((producto, cantidad))

        if not seleccion:
            messages.info(request, "No seleccionaste productos.")
            return redirect('clientes:carrito')

        # Validar stock disponible antes de crear pedido
        for producto, cantidad in seleccion:
            if producto.stock < cantidad:
                messages.error(
                    request,
                    f"No hay stock suficiente para {producto.nombre}. Disponible: {producto.stock}, solicitado: {cantidad}."
                )
                return redirect('clientes:carrito')

        with transaction.atomic():
            pedido = Pedido.objects.create(
                cliente=cliente,
                nombre_cliente_temp=cliente.nombre,
                apellido_cliente_temp=cliente.apellido,
                direccion_temp=cliente.direccion,
                telefono_temp=cliente.telefono,
                tipo_cliente=None,
                estado='PENDIENTE',
            )

            total = Decimal('0.00')
            for producto, cantidad in seleccion:
                subtotal = producto.precio * cantidad
                total += subtotal
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal
                )
                # Descontar stock y guardar
                producto.stock -= cantidad
                producto.save(update_fields=['stock'])

            # Guardar total del pedido
            pedido.monto_total = total
            pedido.save(update_fields=['monto_total'])

            # Crear Tipo de Facturación
            numero_doc = f"PED{pedido.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            facturacion = TipoFacturacion.objects.create(
                pedido=pedido,
                tipo_documento=tipo_factura,
                numero_documento=numero_doc,
                total=total
            )

            # Crear Pago asociado
            metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id)
            Pago.objects.create(
                pedido=pedido,
                metodo_pago=metodo_pago,
                facturacion=facturacion,
                monto=total,
                estado='PENDIENTE'
            )

        # Enviar correo de confirmación al cliente con resumen del pedido
        try:
            if getattr(cliente, 'correo', None):
                subject = "¡Pedido realizado con éxito!"
                nombre_cliente = f"{cliente.nombre} {cliente.apellido}".strip()

                # Construir resumen (texto)
                summary_lines = []
                for producto, cantidad in seleccion:
                    line_subtotal = producto.precio * cantidad
                    summary_lines.append(
                        f"- {producto.nombre}: {cantidad} x ${producto.precio:.2f} = ${line_subtotal:.2f}"
                    )
                resumen_texto = "\n".join(summary_lines)

                # Mensaje de texto plano
                message = (
                    f"¡Hola {nombre_cliente}! \U0001F499\n"
                    f"Tu pedido #{pedido.id} ha sido registrado con éxito en nuestro sistema.\n"
                    f"Nuestro equipo comenzará a preparar tu pedido y te informaremos cuando se encuentre en proceso.\n"
                    f"Te notificaremos vía telefónica ante cualquier inconveniente o actualización sobre tu pedido.\n\n"
                    f"Resumen del pedido:\n{resumen_texto}\n"
                    f"Total: ${total:.2f}\n\n"
                    f"Gracias por confiar en Aguas Paitanás y preferir la pureza que nos caracteriza.\n"
                    f"Estamos felices de poder atenderte y llevarte agua de calidad directamente a tu hogar.\n"
                    f"\U0001F4A7 Aguas Paitanás — pureza que te acompaña siempre.\n\n"
                    f"\u26A0\uFE0F Por favor, no respondas a este correo.\n"
                    f"Este mensaje fue enviado automáticamente por Aguas Paitanás."
                )

                # Construir resumen (HTML)
                rows_html = "".join([
                    f"<tr>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;'>{p.nombre}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:center;'>{c}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right;'>${p.precio:.2f}</td>"
                    f"<td style='padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right;'>${(p.precio*c):.2f}</td>"
                    f"</tr>" for (p, c) in seleccion
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
                        <td style='padding:10px 8px; text-align:right; font-weight:bold;'>${total:.2f}</td>
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

        messages.success(request, "Pedido registrado con éxito. Te notificaremos por correo electrónico cuando esté en proceso.")
        return redirect('clientes:carrito')

    return render(request, 'clientes/carrito.html', {
        'productos': productos,
        'cliente': cliente,
        'metodos_pago': metodos_pago,
        'tipos_factura': tipos_factura,
    })
