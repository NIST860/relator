# Django settings for relator project.

PROJNAME = 'relator'
ROOT = '/home/nate/code/'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ('Nathaniel Soares', 'nathaniel.soares@nist.gov'),
MANAGERS = ADMINS
EMAIL_SENDER = 'nathaniel.soares@nist.gov'

DATABASES = {
	'default': {
			'ENGINE': 'postgresql_psycopg2',
			'NAME': 'main',
			'USER': 'nate',
			'PASSWORD': 'a',
			'HOST': '',
			'PORT': '',
	}
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = True

MEDIA_URL = '/media/'
MEDIA_ROOT = ROOT + PROJNAME + MEDIA_URL
ADMIN_MEDIA_PREFIX = '/media/admin/'

SASS_DIR = MEDIA_ROOT + 'sass/'
CSS_DIR = MEDIA_ROOT + 'css/'
CM_DIR = ROOT + PROJNAME + '/templates/cm/'
HTML_DIR = ROOT + PROJNAME + '/templates/compiled/'

IMAGE_BASE = MEDIA_ROOT + 'images/'
STYLE_BASE = CSS_DIR
SCRIPT_BASE = MEDIA_ROOT + 'js/'

SECRET_KEY = '6(bz^q&0+=2z&3ohzi!qd#2eb3m#f9_gehqe3=pnwv5qyxx*u('

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'relator.urls'

TEMPLATE_DIRS = (
		ROOT + PROJNAME + '/templates/compiled',
		ROOT + PROJNAME + '/templates/html',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.admindocs',
	'django.contrib.admin',
	'django.contrib.databrowse',

	'south',

	'admin',
	'units',
	'data',
	'utilities',
	'constants',
	'zones',
	'windows',
	'locations',
	'standards',
	'structures',
	'components',
	'insulation',
	'lighting',
	'assemblies',
	'cooling',
	'heating',
	'packaged',
	'results',
	'carbon',
	'energy',

	'database',
	'tree',
)
