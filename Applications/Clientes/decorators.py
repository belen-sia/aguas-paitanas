# Applications/Clientes/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def cliente_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('cliente_id'):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('usuarios:iniciarsesion')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
