from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime, timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

secret_file = os.path.join(BASE_DIR, 'secrets.json')
with open(secret_file, 'r') as f:
    secrets = json.loads(f.read())
def get_secret(setting, secrets=secrets): #예외 처리를 통해 오류 발생을 검출합니다.
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)
SECRET_KEY = get_secret("SECRET_KEY")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret("EMAIL")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

API_KEY = get_secret("API_KEY")  # OpenAI

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 액세스 토큰 만료 시간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # 리프레시 토큰 만료 시간
    'ROTATE_REFRESH_TOKENS': True,                 # 리프레시 토큰 회전 여부
    'BLACKLIST_AFTER_ROTATION': True,              # 회전된 리프레시 토큰 블랙리스트 처리 여부
}

# REST_FRAMEWORK 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT 인증 클래스 추가
    ],
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # 액세스 토큰 만료 시간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # 리프레시 토큰 만료 시간
    'ROTATE_REFRESH_TOKENS': True,                   # 리프레시 토큰을 회전시키는지 여부
    'BLACKLIST_AFTER_ROTATION': True,                 # 리프레시 토큰 회전 후 블랙리스트 처리 여부
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  # Django REST framework
    'rest_framework_simplejwt.token_blacklist',  # JWT 블랙리스트 관리
    
    # 'rest_framework','api','django_filters', # searchfilter 넣으면서 같이 추가한 줄

    'accounts',
    'journals',
    'communities',
    'locations',
    'hitcount',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SceneTrip.urls'

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

WSGI_APPLICATION = 'SceneTrip.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # 'locationdata': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'locationdata.sqlite3',
    # }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS' : 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE' : 10,  # 👈 1페이지당 보여줄 갯수
}
# DATABASE_ROUTERS = ['locations.dbrouter.MultiDBRouter']


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# static, media 경로 설정
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'SceneTrip' / 'static'
MEDIA_URL = '/{}/'.format('media')
MEDIA_ROOT= BASE_DIR / 'SceneTrip' / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'