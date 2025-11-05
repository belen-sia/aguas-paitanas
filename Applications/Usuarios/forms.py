from django import forms
from Applications.Clientes.models import Cliente
from .models import Usuario

# -----------------------
# Registro Cliente (autoregisro)
# -----------------------
class ClienteRegisterForm(forms.ModelForm):
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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if not apellido.isalpha():
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido

    def clean_telefono(self):
        import re
        telefono = self.cleaned_data.get('telefono')
        if not re.fullmatch(r'\+569\d{8}', telefono):
            raise forms.ValidationError("El teléfono debe empezar con +569 y contener 8 números adicionales.")
        return telefono


# -----------------------
# Registro Usuario (admin registra trabajadores/repartidores)
# -----------------------
class UsuarioRegisterForm(forms.ModelForm):
    contrasena1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput()
    )
    contrasena2 = forms.CharField(
        label='Repetir contraseña',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'rol']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('contrasena1')
        p2 = cleaned_data.get('contrasena2')
        if p1 != p2:
            self.add_error('contrasena2', 'Las contraseñas no coinciden')
        return cleaned_data


# -----------------------
# Login unificado
# -----------------------
class LoginForm(forms.Form):
    correo = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    contrasena = forms.CharField(
        min_length=4,
        max_length=6,
        error_messages={
            'min_length': 'La contraseña debe tener al menos 4 caracteres.',
            'max_length': 'La contraseña no puede superar los 6 caracteres.'
        },
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'minlength': '4',
            'maxlength': '6'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        correo_input = cleaned_data.get('correo')
        contrasena = cleaned_data.get('contrasena')
        if not correo_input or not contrasena:
            return cleaned_data

        correo_norm = correo_input.strip().lower()

        # Intentar autenticar como Cliente
        cliente = Cliente.objects.filter(correo__iexact=correo_norm).first()
        if cliente:
            if not cliente.check_password(contrasena):
                raise forms.ValidationError('Correo o contraseña incorrectos')
            cleaned_data['auth_kind'] = 'cliente'
            cleaned_data['user_obj'] = cliente
            cleaned_data['correo_norm'] = correo_norm
            return cleaned_data

        # Intentar autenticar como Usuario (custom user)
        usuario = Usuario.objects.filter(email__iexact=correo_norm).first()
        if usuario:
            if not usuario.check_password(contrasena):
                raise forms.ValidationError('Correo o contraseña incorrectos')
            cleaned_data['auth_kind'] = 'usuario'
            cleaned_data['user_obj'] = usuario
            cleaned_data['correo_norm'] = correo_norm
            return cleaned_data

        # No existe ni como cliente ni como usuario
        raise forms.ValidationError('Correo o contraseña incorrectos')

