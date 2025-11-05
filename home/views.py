from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from Applications.Clientes.forms import ClienteForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from . import views
from django.core.mail import send_mail
from django.conf import settings


class InicioIndexView(TemplateView):
    template_name = 'home/inicioindex.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RegistrarView(View):
    template_name = 'home/registrar.html'

    def get(self, request, *args, **kwargs):
        form = ClienteForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
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
                    send_mail(subject, message, from_email, [cliente.correo], fail_silently=True, html_message=html_message)
            except Exception:
                pass
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('usuarios:iniciarsesion')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
        return render(request, self.template_name, {'form': form})


class ContactoView(TemplateView):
    template_name = 'home/contacto.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CerrarsesionView(TemplateView):
    template_name = 'home/cerrarsesion.html'

class PortalClientesView(LoginRequiredMixin, View):
    template_name = 'clientes/portalclientes.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)