# Django settings for scenable project.
import os

# import settings that differ based on deployment
import settings_local

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SITE_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))


def project_file(path):
    '''prepends PROJECT_ROOT setting to the given path'''
    return os.path.join(PROJECT_ROOT, path)


def site_file(path):
    '''prepends SITE_ROOT setting to the given path'''
    return os.path.join(SITE_ROOT, path)


DEBUG = settings_local.DEBUG
TEMPLATE_DEBUG = settings_local.TEMPLATE_DEBUG

ADMINS = settings_local.ADMINS
MANAGERS = settings_local.MANAGERS

DATABASES = {
    'default': settings_local.DB_DEFAULT
}
DATABASES['default']['TEST_CHARSET'] = 'utf8'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = settings_local.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = settings_local.STATIC_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    project_file('resources'),
    project_file('boilerplate'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!)6pq@7zn=+*tf(&amp;gngk*b)^*8r)b44yg3!10)3$^p9r%&amp;ppme'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'scenable.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'scenable.wsgi.application'

TEMPLATE_DIRS = (
    project_file('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    'sorl.thumbnail',
    'pipeline',
    'tastypie',
    'haystack',
    'django_extensions',
    'scenable.common',
    'scenable.accounts',
    'scenable.tags',
    'scenable.places',
    'scenable.organizations',
    'scenable.events',
    'scenable.specials',
    'scenable.news',
    'scenable.chatter',
    'scenable.feedback',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# (see master:687f9565 for old logging examples)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': site_file('logs/debug.log')
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'debugging': {
            'handlers': ['console', 'debug_file'],
            'level': 'DEBUG',
            'propagate': False
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    }
}

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

FIXTURE_DIRS = (
    project_file('fixtures'),
)

# email settings for production errors
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
SERVER_EMAIL = settings_local.SERVER_EMAIL
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS
SEND_BROKEN_LINK_EMAILS = True

# pipeline settings
from settings_pipeline import *
# this is defined outside so we can use project_file
PIPELINE_YUI_BINARY = project_file('../bin/yuicompressor')
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

# initial Haystack setup for Whoosh
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': project_file('../var/whoosh_index'),
    },
}
