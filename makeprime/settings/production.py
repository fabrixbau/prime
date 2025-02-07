from .base import *
import os

DEBUG = False
# Usa una variable de entorno para la SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-secret-key')  # Asegúrate de definir 'DJANGO_SECRET_KEY' en tu entorno

# Define los hosts permitidos
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

# Configuración de la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'db_prime'),
        'USER': os.environ.get('DB_USER', 'ubuntu'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'default_password'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}