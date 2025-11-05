# Applications/Usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'username', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'rol')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'rol', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)
