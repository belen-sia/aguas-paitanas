from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from .forms import ClienteRegisterForm, LoginForm
from Applications.Clientes.models import Cliente
from .models import Usuario
from django.db.models import Q


# -----------------------
# Registro cliente (auto-registro)
# -----------------------
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteRegisterForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.set_password(form.cleaned_data['contrasena'])
            cliente.save()
            messages.success(request, f"Cliente {cliente.nombre} registrado exitosamente")
            return redirect('usuarios:iniciarsesion')
    else:
        form = ClienteRegisterForm()
    return render(request, 'home/registrar.html', {'form': form})


# -----------------------
# Login unificado (Clientes + Usuarios)
# -----------------------
def iniciar_sesion(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        auth_kind = form.cleaned_data.get('auth_kind')
        user_obj = form.cleaned_data.get('user_obj')
        correo_norm = form.cleaned_data.get('correo_norm')
        contrasena = form.cleaned_data.get('contrasena')

        # Autenticación como Cliente (manejado con sesión propia)
        if auth_kind == 'cliente' and user_obj:
            request.session['cliente_id'] = user_obj.id
            request.session['rol'] = 'CLIENTE'
            return redirect('clientes:portalclientes')

        # Autenticación como Usuario (usar backend de Django)
        if auth_kind == 'usuario' and user_obj:
            user = authenticate(request, username=correo_norm, password=contrasena)
            if user is not None:
                django_login(request, user)
                request.session['rol'] = getattr(user, 'rol', None)

                # Superusuario: enviar siempre al portal de administrador
                if getattr(user, 'is_superuser', False):
                    return redirect('trabajadores:portaladministrador')

                # Redirecciones por rol (para usuarios no superusuarios)
                if getattr(user, 'rol', None) == 'ADMIN':
                    return redirect('trabajadores:portaladministrador')
                elif getattr(user, 'rol', None) == 'TRAB':
                    return redirect('trabajadores:portaltrabajadores')
                elif getattr(user, 'rol', None) == 'REPAR':
                    # Mapear usuario->repartidor por correo y guardar en sesión
                    try:
                        from Applications.Repartidores.models import Repartidor
                        rep = Repartidor.objects.filter(correo_electronico__iexact=user.email).first()
                        if rep:
                            request.session['repartidor_id'] = rep.id
                    except Exception:
                        pass
                    return redirect('repartidores:portalrepartidores')
                else:
                    return redirect('/')

            messages.error(request, "Contraseña incorrecta para usuario")
            return render(request, 'home/iniciarsesion.html', {'form': form})

        # Si el formulario es válido pero no trajo credenciales válidas
        messages.error(request, "Correo o contraseña incorrectos")
        return render(request, 'home/iniciarsesion.html', {'form': form})

    return render(request, 'home/iniciarsesion.html', {'form': form})


# -----------------------
# Cerrar sesión
# -----------------------
def cerrar_sesion(request):
    django_logout(request)
    # Limpiar claves de sesión usadas para clientes no autenticados por Django
    request.session.pop('cliente_id', None)
    request.session.pop('rol', None)
    messages.info(request, "Sesión cerrada correctamente")
    return redirect('usuarios:iniciarsesion')


# -----------------------
# Gestión de Usuarios (redirigir al admin de Django)
# -----------------------
def gestion_usuarios(request):
    query = request.GET.get('q', '').strip()
    usuarios = Usuario.objects.all()
    if query:
        usuarios = usuarios.filter(
            Q(email__icontains=query) |
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    return render(request, 'gestion/gestion_usuarios.html', {"usuarios": usuarios})


# -----------------------
# Registrar usuario (trabajador/repartidor/admin)
# -----------------------
def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        rol = request.POST.get('rol')
        p1 = request.POST.get('contrasena1')
        p2 = request.POST.get('contrasena2')
        is_active_val = request.POST.get('is_active', '1')

        if not all([username, email, first_name, last_name, rol, p1, p2]):
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('usuarios:gestion_usuarios')
        if p1 != p2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('usuarios:gestion_usuarios')
        if not (4 <= len(p1) <= 6):
            messages.error(request, 'La contraseña debe tener entre 4 y 6 caracteres')
            return redirect('usuarios:gestion_usuarios')

        if Usuario.objects.filter(Q(email__iexact=email) | Q(username__iexact=username)).exists():
            messages.error(request, 'Ya existe un usuario con ese email o username')
            return redirect('usuarios:gestion_usuarios')

        user = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            rol=rol,
            is_active=True if is_active_val in ('1', 'true', 'on') else False,
            is_staff=True if rol == 'ADMIN' else False,
        )
        user.set_password(p1)
        user.save()
        rol_verbose = dict(Usuario.ROLES).get(rol, 'Usuario')
        messages.success(request, f'¡{rol_verbose} registrado con éxito!')
        return redirect('usuarios:gestion_usuarios')

    return redirect('usuarios:gestion_usuarios')


# -----------------------
# Editar usuario
# -----------------------
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        usuario.username = request.POST.get('username', usuario.username).strip()
        usuario.email = request.POST.get('email', usuario.email).strip().lower()
        usuario.first_name = request.POST.get('first_name', usuario.first_name).strip()
        usuario.last_name = request.POST.get('last_name', usuario.last_name).strip()
        usuario.rol = request.POST.get('rol', usuario.rol)
        is_active = request.POST.get('is_active')
        usuario.is_active = True if is_active in ('on', 'true', '1') else False
        usuario.is_staff = True if usuario.rol == 'ADMIN' else usuario.is_staff
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('usuarios:gestion_usuarios')

    return redirect('usuarios:gestion_usuarios')


# -----------------------
# Eliminar usuario
# -----------------------
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('usuarios:gestion_usuarios')
    return redirect('usuarios:gestion_usuarios')

