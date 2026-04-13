from pathlib import Path
from datetime import timedelta
import os
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {'1', 'true', 'yes', 'on'}


def env_int(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return int(value)

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] if DEBUG else ['yourdomain.com']

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',

    'apps.accounts',
    'apps.events',
    'apps.tickets',
    'apps.payments',
    'apps.organizer',
    'apps.notifications',
    'apps.admin_panel',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'planova.urls'
WSGI_APPLICATION = 'planova.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'planova_db',
        'USER': 'planova',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_HSTS_SECONDS = env_int('SECURE_HSTS_SECONDS', 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', True)
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env_int('JWT_ACCESS_TOKEN_MINUTES', 15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env_int('JWT_REFRESH_TOKEN_DAYS', 7)),
    'ROTATE_REFRESH_TOKENS': env_bool('JWT_ROTATE_REFRESH_TOKENS', True),
    'BLACKLIST_AFTER_ROTATION': env_bool('JWT_BLACKLIST_AFTER_ROTATION', True),
    'UPDATE_LAST_LOGIN': env_bool('JWT_UPDATE_LAST_LOGIN', True),
    'ALGORITHM': os.environ.get('JWT_ALGORITHM', 'HS256'),
    'SIGNING_KEY': os.environ.get('JWT_SIGNING_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': (os.environ.get('JWT_AUTH_HEADER_TYPE', 'Bearer'),),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_OBTAIN_SERIALIZER': 'apps.accounts.serializers.LoginSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'apps.accounts.serializers.RefreshTokenSerializer',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Planova API',
    'DESCRIPTION': 'API documentation for Planova project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': False,
        'persistAuthorization': True,
    },
    'TAGS': [
        {'name': 'System', 'description': 'Operational endpoints'},
        {'name': 'Authentication', 'description': 'Account registration, login, logout, and profile management'},
        {'name': 'Events', 'description': 'Event catalog, categories, favorites, and reviews'},
        {'name': 'Organizer', 'description': 'Organizer profile and dashboard endpoints'},
        {'name': 'Tickets', 'description': 'Ticket types, tickets, and check-in flows'},
        {'name': 'Payments', 'description': 'Payment history, checkout, and webhooks'},
        {'name': 'Notifications', 'description': 'User notification endpoints'},
        {'name': 'Admin Panel', 'description': 'Administrative reporting and resource management'},
    ],
    'ENUM_NAME_OVERRIDES': {
        'UserRoleEnum': 'apps.accounts.models.User.Role',
        'EventStatusEnum': 'apps.events.models.Event.Status',
        'EventTypeEnum': 'apps.events.models.Event.EventType',
        'PaymentStatusEnum': 'apps.payments.models.Payment.Status',
        'PaymentProviderEnum': 'apps.payments.models.Payment.Provider',
        'TicketStatusEnum': 'apps.tickets.models.Ticket.Status',
        'NotificationTypeEnum': 'apps.notifications.models.Notification.Type',
    },
}

STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

DEFAULT_FROM_EMAIL = 'noreply@planova.com'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_TIMEOUT = env_int('SENDGRID_TIMEOUT', 10)
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', DEFAULT_FROM_EMAIL)

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'send-upcoming-event-reminders-every-hour': {
        'task': 'apps.notifications.tasks.queue_event_reminder_emails',
        'schedule': crontab(minute=0),
    },
}
