"""
Django settings for mealmatcher_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


STATIC_PATH = os.path.join(BASE_DIR,'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    STATIC_PATH,
)


TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

# templates
TEMPLATE_DIRS = ( 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    TEMPLATE_PATH,
    )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dxqjz7r(f!+zh#)q=8i^_p54s*b$8+(fz0!imzcq7ip)@9c48t'

# SECURITY WARNING: don't run with debug turned on in production!
# Kept on due to issues with server hosting. 
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'mealmatcher.herokuapp.com']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mealmatcher_app',
    'post_office',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mealmatcher_project.urls'

WSGI_APPLICATION = 'mealmatcher_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

### HEROKU DB SETTINGS: Comment this out when running on local, but uncomment when using these settings to run on heroku
# import dj_database_url
# DATABASES = {}
# DATABASES['default'] =  dj_database_url.config(default='postgres://wwzrrmdkhlzakt:rM3Ux-GV8H67N1WGgNGXuOG4tV@ec2-54-163-226-9.compute-1.amazonaws.com:5432/dc8nuaqi4u7f5')
# DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
### end of Heroku server db settings

# LOCAL DB SETTINGS: Comment this when running on heroku, but uncomment and use this for running on local
# Please note: You will need to setup a localhost database at port 5432 with name mealmatcher_db, user mealmatcher_db,
#               and password (matching below) in order to run the website locally.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mealmatcher_db',
        'USER': 'mealmatcher_user',
        'PASSWORD': '*****',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

### end of local server db settings

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True



## Added the Email Backend
EMAIL_BACKEND = 'post_office.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'princeton.meal.matcher@gmail.com'
EMAIL_HOST_PASSWORD = '*****'
#EMAIL_HOST_PASSWORD = 'i8wsuHLt5PmaXkxB8Ok7qg'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Redirects non-logged in users to this
LOGIN_URL = '/login/'

'''
# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
'''