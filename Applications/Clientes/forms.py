from django import forms
from .models import Cliente
import re

class ClienteForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=4,
        max_length=6,
        error_messages={
            'min_length': 'La contraseña debe tener al menos 4 caracteres.',
            'max_length': 'La contraseña no puede superar los 6 caracteres.'
        }
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'direccion', 'telefono', 'correo', 'contrasena', 'tipo_cliente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # En edición (cuando hay instancia), la contraseña es opcional
        if getattr(self.instance, 'pk', None):
            self.fields['contrasena'].required = False

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Permite letras con acentos y espacios
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+", nombre or ""):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        # Permite letras con acentos y espacios (apellidos compuestos)
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+", apellido or ""):
            raise forms.ValidationError("El apellido solo puede contener letras y espacios.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono') or ""
        # Rechaza cualquier letra
        if re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]", telefono):
            raise forms.ValidationError("El teléfono no puede contener letras.")
        # Chile: exigir formato +569XXXXXXXX (8 dígitos después de 569)
        if not re.fullmatch(r"\+569\d{8}", telefono):
            raise forms.ValidationError("El teléfono debe empezar con +569 y contener 8 números adicionales.")
        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not re.fullmatch(r'[A-Za-z0-9# ]+', direccion):
            raise forms.ValidationError("La dirección solo puede contener letras, números y '#'.")
        return direccion

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if '@' not in correo:
            raise forms.ValidationError("El correo debe contener '@'.")
        return correo

    def save(self, commit=True):
        cliente = super().save(commit=False)
        contrasena = self.cleaned_data.get("contrasena")
        # Solo actualizar contraseña si el usuario ingresó una
        if contrasena:
            cliente.set_password(contrasena)
        if commit:
            cliente.save()
        return cliente

