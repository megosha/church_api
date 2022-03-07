import os
import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

ALLOWED_HOSTS = ['*']
SESSION_COOKIE_DOMAIN = '.church22.ru'
SESSION_COOKIE_NAME = env.str('SESSION_COOKIE_NAME', 'tmp.church22.ru' if DEBUG else 'church22.ru')
SESSION_COOKIE_AGE = 7777777  # 90 days

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'mailing.apps.MailingConfig',
    'api.apps.ApiConfig',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'solo',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.instagram',
    # 'allauth.socialaccount.providers.odnoklassniki',
    'allauth.socialaccount.providers.vk',
    'sorl.thumbnail',
    'django_celery_beat',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'front.middleware.SiteSelectMiddleware',
]

ROOT_URLCONF = 'church_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'church_api.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Barnaul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_DIRS = [os.path.join(BASE_DIR, "church_api", "static")]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ORIGIN_ALLOW_ALL = True

ADMINS = ('Andrey', 'andrey@electis.ru'),
LOG_PATH = os.path.join(BASE_DIR, "logs")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'}
    },
    'handlers': {
        'django_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'django_error.log'),
            'formatter': 'standard'
        },
        'info': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'django_info.log'),
            'formatter': 'standard'
        },
        'other': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'other.log'),
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['info', 'django_error'],
            'level': 'INFO',
            'propagate': True,
        },
        'api.tasks': {
            'handlers': ['other',],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='smtp://user@:password@localhost:25')
vars().update(EMAIL_CONFIG)
DEFAULT_FROM_EMAIL = EMAIL_CONFIG.get('EMAIL_HOST_USER')

ROBOKASSA_LOGIN = env.str('ROBOKASSA_LOGIN', '')
ROBOKASSA_PASS1 = env.str('ROBOKASSA_PASS1', '')

LOGIN_REDIRECT_URL = '/profile'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    # 'front.backends.EmailAuthBackend',
)

SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

TGRAM_TOKEN = env.str('TGRAM_TOKEN', '')
TGRAM_PHRAZE = env.str('TGRAM_PHRAZE', '')

GOOGLE_API_KEY = env.str('GOOGLE_API_KEY', '')

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_TIMEZONE = 'Asia/Barnaul'

TTP_ID = env.str('TTP_ID', '')
TTP_TEXT = env.str('TTP_TEXT', '')

FEEDBACK_EMAILS = env.list('FEEDBACK_EMAILS', default=None)
