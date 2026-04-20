from django.contrib.messages import constants as messages
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-hsbs-root-key'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'simple_history', 'django_bootstrap5', 'core',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', 'simple_history.middleware.HistoryRequestMiddleware',
]
ROOT_URLCONF = 'setup.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Altere para esta linha exata
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': BASE_DIR / 'db.sqlite3'}}
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
# --- Configurações de Arquivos Estáticos ---
STATIC_URL = 'static/'

# Pasta onde você coloca seus arquivos (logo, etc.)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Pasta onde o Django reunirá tudo (Resolve o erro ImproperlyConfigured)
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configurações de Acesso ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'registro_list'
LOGOUT_REDIRECT_URL = 'login'

MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
