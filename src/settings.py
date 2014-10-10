# coding: utf-8
"""
Django settings for minitickets project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings as DEFAULT_SETTINGS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f2$ja%ajh+*2en_+1kwbu37ky(1x7vn3=(qbap&k(2a@xxcgvn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Other Apps
    'south',
    'django_tables2',
    'rest_framework',

    'lib.utils.html',
    'lib.utils.forms',
    'lib.utils.tables',

    # Project Apps
    'src.minitickets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lib.utils.middlewares.ApplicationMiddleware',
)

ROOT_URLCONF = 'src.urls'

WSGI_APPLICATION = 'src.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pt-br'

LANGUAGES = (
    ('pt_BR', u'Português'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.contrib.messages.context_processors.messages",

    # application context processors
    "lib.utils.views.context_processors.page_settings_context_processor",
    "lib.utils.context_processors.date_context_processor",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


TEMPLATE_DIRS = (
    (os.path.join('templates')),
)

# Redirect and login definition
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Bootstrap icon support
ICON_PREFIX = 'fa-'
ICON_BASE_ATTRS = {'class': 'fa'}

# Session
SESSION_COOKIE_NAME = 'minitickets'

# User Model
AUTH_USER_MODEL = 'minitickets.Funcionario'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ( 'rest_framework.authentication.TokenAuthentication', ),
    'DEFAULT_PERMISSION_CLASSES': ( 'rest_framework.permissions.AllowAny', )
}