from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# Secrets.json
secret_file = os.path.join(BASE_DIR, 'secrets.json')
with open(secret_file, 'r') as f:
    secrets = json.loads(f.read())
def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

# API KEY
SECRET_KEY = get_secret("SECRET_KEY")
API_KEY = get_secret("API_KEY")  # OpenAI
NAVER_CLIENT_ID = get_secret("NAVER_CLIENT_ID") # Naver search Client Id
NAVER_SECRET_KEY = get_secret("NAVER_SECRET_KEY") # Naver Search API Secret Key
KAKAO_REST_API_KEY = get_secret("KAKAO_REST_API_KEY") # Kakao Rest API key
KAKAO_JAVA_SCRIPTS_API_KEY = get_secret("KAKAO_JAVA_SCRIPTS_API_KEY") # Kakao javascripts key
# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret("EMAIL")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
MANAGER_EMAIL = get_secret("MANAGER_EMAIL")  # 관리자의 이메일 주소

# SECURITY WARNING: don't run with debug turned on in production!
# 배포 시 False
DEBUG = True

# Hosts
ALLOWED_HOSTS = []


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),  # 액세스 토큰 만료 시간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # 리프레시 토큰 만료 시간
    'ROTATE_REFRESH_TOKENS': True,                   # 리프레시 토큰을 회전시키는지 여부
    'BLACKLIST_AFTER_ROTATION': True,                 # 리프레시 토큰 회전 후 블랙리스트 처리 여부
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Application definition
INSTALLED_APPS = [
    # 기본 Django 앱들
    'daphne',  # asgi
    'channels',  # 채널
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # allauth 관련 app

    # 외부 앱들
    'corsheaders',
    'rest_framework',  # Django REST framework
    'rest_framework.authtoken',  # authtoken 추가
    'rest_framework_simplejwt.token_blacklist',  # JWT 블랙리스트 관리

    # 외부앱(allauth)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.kakao',  # Kakao 제공자

    # 자체 앱들
    'accounts',
    'chats',
    'journals',
    'communities',
    'locations',
    'questions',
    
    # 조회수
    'hitcount',
]

# BASE_URL 주소
BASE_URL = 'http://127.0.0.1:8000'

# 사이트
SITE_ID = 1

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [ 
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 미들웨어 추가
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.ContentTypeOptionsMiddleware', 
]

SESSION_COOKIE_SECURE = False 
SESSION_ENGINE = 'django.contrib.sessions.backends.db' 

SECURE_CONTENT_TYPE_NOSNIFF = True

### CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # 모든 도메인에서 요청 허용

CORS_ALLOW_METHODS = [  # 허용할 옵션
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [ # 허용할 헤더
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-requested-with",
]

CORS_ALLOW_ALL_ORIGINS = True  # 모든 도메인에서 요청 허용
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = []
###



ROOT_URLCONF = 'SceneTrip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'SceneTrip.wsgi.application'
ASGI_APPLICATION = 'SceneTrip.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': (
    # 'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS' : 'rest_framework.pagination.PageNumberPagination', # 페이지네이션
    'PAGE_SIZE' : 10,  # 👈 1페이지당 보여줄 갯수
}

REST_AUTH = {
    'USE_JWT' : True,
    'JWT_EXPIRATION_DELTA': timedelta(days=1),
    'JWT_AUTH_COOKIE' : 'access',
    'JWT_AUTH_HTTPONLY': True,
    'JWT_AUTH_REFRESH_COOKIE' : "refresh_token",
    'JWT_AUTH_SAMESITE': 'Lax',
    'JWT_AUTH_COOKIE_USE_CSRF' : False,
    'SESSION_LOGIN' : False
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

LOGIN_URL = '/api/accounts/login/'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
