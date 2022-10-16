import os
import sys
import logging
import shutil

from datetime import timedelta
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

from agm_env_helper.env_helper import get_env_var
from project.logger import CustomisedJSONFormatter

BASE_DIR = Path(__file__).resolve().parent.parent

# Create directories for logs
paths = [
    'logs',
    'media',
    '../frames',
]
for path in paths:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory '{path}' was created.")

logger = logging.getLogger(__name__)

load_dotenv()
DATA_UPLOAD_MAX_NUMBER_FIELDS = None
# --- Core Backend ---
# - Main
DEBUG = get_env_var(bool, 'BACKEND_DEBUG_MODE', True)
SECRET_KEY = get_env_var(str, 'BACKEND_SECRET_KEY', DEBUG)
ALLOWED_HOSTS = get_env_var(str, 'BACKEND_ALLOWED_HOSTS', DEBUG).split(' ')
# --- Database
BACKEND_DEFAULT_DB = get_env_var(str, 'BACKEND_DEFAULT_DB', DEBUG)
DB_NAME = get_env_var(str, 'DB_NAME', DEBUG)
DB_USER = get_env_var(str, 'DB_USER', DEBUG)
DB_PASSWORD = get_env_var(str, 'DB_PASSWORD', DEBUG)
DB_HOST = get_env_var(str, 'DB_HOST', DEBUG)

LOG_PATH = os.path.join(BASE_DIR, 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "json": {
            '()': CustomisedJSONFormatter,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'app_log_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'app.log.json'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'app_log_file'],
        'level': 'DEBUG',
    },
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework.authtoken',
    'rest_framework',
    'corsheaders',
    'djoser',
    'drf_yasg',

    'main_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project.wsgi.application'

# Database


if BACKEND_DEFAULT_DB == 'SQLite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif BACKEND_DEFAULT_DB == 'PostgreSQL':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': 5432,
        }
    }
else:
    logging.error(f"ERROR: BACKEND_DEFAULT_DB env variable has wrong value. Value must be 'PostgreSQL' or 'SQLite'. \
        Current value is '{BACKEND_DEFAULT_DB}'.")
    sys.exit()

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static_django/'
STATIC_ROOT = os.path.join(os.path.abspath(os.curdir), 'static_django')

MEDIA_ROOT = str(BASE_DIR) + '/media/'
MEDIA_URL = '/media/'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = False
CSRF_TRUSTED_ORIGINS = [
    'https://dev.reality-x.ru',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]
CORS_ORIGIN_WHITELIST = [
    'https://dev.reality-x.ru',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

DJOSER = {
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/?uid={uid}&token={token}',
    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/?uid={uid}&token={token}',
    'SEND_ACTIVATION_EMAIL': True,
    'LOGIN_FIELD': 'email'
}

print('---')
