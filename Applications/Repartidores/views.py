from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from Applications.Pedidos.models import Pedido
from Applications.Repartidores.models import NotificacionRepartidor


def portalrepartidores(request):
    # Mostrar notificaciones pendientes al entrar al portal
    email = _repartidor_email(request)
    if email:
        pendientes = list(NotificacionRepartidor.objects.filter(correo_electronico__iexact=email, leida=False).order_by('created_at'))
        for n in pendientes:
            messages.info(request, n.mensaje)
        if pendientes:
            NotificacionRepartidor.objects.filter(id__in=[n.id for n in pendientes]).update(leida=True)
    return render(request, 'repartidores/portalrepartidores.html')


def _repartidor_email(request):
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False) and getattr(user, 'rol', None) == 'REPAR' and getattr(user, 'email', None):
        return user.email
    return None


def pedidos_asignados(request):
    email = _repartidor_email(request)
    if not email:
        messages.error(request, 'No autorizado')
        return redirect('repartidores:portalrepartidores')

    # Mostrar notificaciones pendientes también aquí, por si entra directo
    pendientes = list(NotificacionRepartidor.objects.filter(correo_electronico__iexact=email, leida=False).order_by('created_at'))
    for n in pendientes:
        messages.info(request, n.mensaje)
    if pendientes:
        NotificacionRepartidor.objects.filter(id__in=[n.id for n in pendientes]).update(leida=True)

    pedidos = Pedido.objects.filter(
        repartidor__correo_electronico__iexact=email
    ).exclude(estado='CANCELADO')
    estados = [(val, label) for val, label in Pedido.ESTADOS if val in ('PENDIENTE', 'EN_PROCESO', 'ENTREGADO')]

    return render(request, 'repartidores/pedidos_asignados.html', {
        'pedidos': pedidos,
        'ESTADOS': estados,
    })


def actualizar_estado_repartidor(request, pedido_id):
    email = _repartidor_email(request)
    if not email:
        messages.error(request, 'No autorizado')
        return redirect('repartidores:portalrepartidores')

    pedido = get_object_or_404(Pedido, id=pedido_id)
    rep_mail = getattr(getattr(pedido, 'repartidor', None), 'correo_electronico', None)
    if not rep_mail or rep_mail.lower() != email.lower():
        return HttpResponseForbidden('No puedes modificar este pedido')

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = dict(Pedido.ESTADOS)
        if nuevo_estado in estados_validos:
            from datetime import date
            if nuevo_estado == 'ENTREGADO' and pedido.fecha_entrega is None:
                pedido.fecha_entrega = date.today()
            elif nuevo_estado != 'ENTREGADO':
                pedido.fecha_entrega = None
            pedido.estado = nuevo_estado
            pedido.save(update_fields=['estado', 'fecha_entrega'])

            # Enviar correo al cliente cuando el repartidor cambia a EN_PROCESO o ENTREGADO
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

                    if subject and message and html_message:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@localhost')
                        send_mail(subject, message, from_email, [cliente.correo], fail_silently=False, html_message=html_message)
                except Exception:
                    pass

            messages.success(request, f"Pedido #{pedido.id} actualizado a {estados_validos[nuevo_estado]}.")
    return redirect('repartidores:pedidos_asignados')


def historial_entregas(request):
    email = _repartidor_email(request)
    if not email:
        messages.error(request, 'No autorizado')
        return redirect('repartidores:portalrepartidores')

    pedidos = Pedido.objects.filter(
        repartidor__correo_electronico__iexact=email,
        estado='ENTREGADO'
    )
    return render(request, 'repartidores/historial_entregas.html', {
        'pedidos': pedidos,
    })
