from AguasPaitanas.settings.base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Email configuration (Gmail SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "aguapurificadapaitanas@gmail.com"
EMAIL_HOST_PASSWORD = "mgqzvbzcananyecg"
EMAIL_TIMEOUT = 30
DEFAULT_FROM_EMAIL = "Aguas Paitanás <aguapurificadapaitanas@gmail.com>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME":  "aguaspaitanas",
        "USER": "belen",
        "PASSWORD": "belen1",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.INFO: 'info',
    messages.WARNING: 'warning',
}

AUTH_USER_MODEL = 'Usuarios.Usuario'  # Tu modelo personalizado
LOGIN_REDIRECT_URL = 'redirigir_por_rol'  # Redirige según rol
LOGOUT_REDIRECT_URL = 'iniciarsesion'
LOGIN_URL = 'usuarios:iniciarsesion'

AUTHENTICATION_BACKENDS = [
    'Applications.Usuarios.backends.EmailBackend',
    'Applications.Usuarios.backends.ClienteBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
