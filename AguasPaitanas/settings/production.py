from AguasPaitanas.settings.base import *
import os
import dj_database_url
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 🚫 Seguridad
DEBUG = False
ALLOWED_HOSTS = ['aguas-paitanas.onrender.com', 'localhost', '127.0.0.1']

# 📦 Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Whitenoise para servir archivos estáticos en producción
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# 📧 Configuración de correo (usa las mismas que local o variables de entorno)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='aguapurificadapaitanas@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='mgqzvbzcananyecg')
EMAIL_TIMEOUT = 30
DEFAULT_FROM_EMAIL = "Aguas Paitanás <aguapurificadapaitanas@gmail.com>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# 🗃️ Base de datos — Railway crea DATABASE_URL automáticamente
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# 📁 Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 🧩 Configuración de usuarios personalizada (igual que en local)
AUTH_USER_MODEL = 'Usuarios.Usuario'
LOGIN_REDIRECT_URL = 'redirigir_por_rol'
LOGOUT_REDIRECT_URL = 'iniciarsesion'
LOGIN_URL = 'usuarios:iniciarsesion'

AUTHENTICATION_BACKENDS = [
    'Applications.Usuarios.backends.EmailBackend',
    'Applications.Usuarios.backends.ClienteBackend',
    'django.contrib.auth.backends.ModelBackend',
]

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.INFO: 'info',
    messages.WARNING: 'warning',
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
