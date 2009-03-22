# Django settings for rbwebsite project.
import os
import sys


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Christian Hammond', 'chipx86@chipx86.com'),
)

MANAGERS = ADMINS

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware', # Keep this first,
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.CacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'djblets.util.context_processors.mediaSerial'
)

ROOT_URLCONF = 'rbwebsite.urls'

RBWEBSITE_ROOT = os.path.abspath(os.path.dirname(__file__))

TEMPLATE_DIRS = (
    os.path.join(RBWEBSITE_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'djblets.gravatars',
    'djblets.util',
    'rbwebsite.blogfeeds',
    'rbwebsite.docs',
    'rbwebsite.donations',
    'rbwebsite.happyusers',
    'rbwebsite.news',
    'rbwebsite.press',
    'rbwebsite.releases',
    'rbwebsite.screenshots',
    'rbwebsite.search',
)

WEB_API_ENCODERS = (
    'djblets.webapi.core.BasicAPIEncoder',
)


# Default expiration time for the cache.  Note that this has no effect unless
# CACHE_BACKEND is specified in settings_local.py
CACHE_EXPIRATION_TIME = 60 * 60 * 24 * 30 # 1 month


# Dependency checker functionality.  Gives our users nice errors when they start
# out, instead of encountering them later on.  Most of the magic for this
# happens in manage.py, not here.
if os.path.split(os.path.dirname(__file__))[1] != 'rbwebsite':
    sys.stderr.write('The directory containing manage.py must be '
                     'named "rbwebsite"\n')
    sys.exit(1)

# Load local settings.  This can override anything in here, but at the very
# least it needs to define database connectivity.
try:
    import settings_local
    from settings_local import *
except ImportError:
    sys.stderr.write('Unable to read settings_local.py.\n')
    sys.exit(1)

TEMPLATE_DEBUG = DEBUG

LOCAL_ROOT = os.path.dirname(settings_local.__file__)
HTDOCS_ROOT = os.path.join(LOCAL_ROOT, "..", "htdocs")
MEDIA_ROOT = os.path.join(HTDOCS_ROOT, "media")
MEDIA_URL = "/media/"
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'

MEDIA_SERIAL_DIRS = ["admin", "rbsite"]
