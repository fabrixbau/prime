from .base import *
from decouple import config

DEBUG = True

# Lee las variables del archivo .env
SECRET_KEY = config('DJANGO_SECRET_KEY', default='default-secret-key')
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost').split(',')

# Configuración de la base de datos para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

