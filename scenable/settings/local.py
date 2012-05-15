DEBUG = True
TEMPLATE_DEBUG = DEBUG

DB_DEFAULT = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'obiddev',
    #'NAME': 'obid_sandbox',
    'USER': 'postgres',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}

# DB_DEFAULT = {
#     'ENGINE': 'django.db.backends.mysql',
#     'NAME': 'obid_mysqltest',
#     'USER': 'root',
#     'PASSWORD': 'root',
#     'HOST': '',
#     'PORT': '',
# }

MEDIA_ROOT = '/Users/gdn/Sites/public/scenable/media'
STATIC_ROOT = '/Users/gdn/Sites/public/scenable/static'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'greg@scenable.com'
EMAIL_HOST_PASSWORD = 'CrabCakesHaveNoFrosting'
DEFAULT_FROM_EMAIL = 'Scenable Robot <robot@scenable.com>'
SERVER_EMAIL = 'robot@scenable.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
