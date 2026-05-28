from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────
#  Основные настройки
# ──────────────────────────────────────────────
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-xxx-change-me')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

SITE_NAME = 'TeamFinder'
TASK_VERSION = config('TASK_VERSION', default='1')


# ──────────────────────────────────────────────
#  Приложения
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Локальные
    'users.apps.UsersConfig',
    'projects.apps.ProjectsConfig',
]


# ──────────────────────────────────────────────
#  Middleware
# ──────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ──────────────────────────────────────────────
#  URLs и WSGI
# ──────────────────────────────────────────────
ROOT_URLCONF = 'team_finder.urls'
WSGI_APPLICATION = 'team_finder.wsgi.application'


# ──────────────────────────────────────────────
#  Шаблоны
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / f'templates_var{TASK_VERSION}'],
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


# ──────────────────────────────────────────────
#  База данных (PostgreSQL)
# ──────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='teamfinder'),
        'USER': config('POSTGRES_USER', default='teamfinder'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='teamfinder'),
        'HOST': config('POSTGRES_HOST', default='localhost'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}


# ──────────────────────────────────────────────
#  Валидация паролей
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ──────────────────────────────────────────────
#  Язык и время
# ──────────────────────────────────────────────
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────────
#  Статические файлы и медиа
# ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ──────────────────────────────────────────────
#  Кастомная модель пользователя
# ──────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/projects/list/'
LOGOUT_REDIRECT_URL = '/projects/list/'


# ──────────────────────────────────────────────
#  Прочее
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'