import os
from decouple import config, Csv
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv



load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if os.name == 'nt':
    OSGEO4W_ROOT = r"C:\OSGeo4W"
    os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + os.pathsep + os.environ['PATH']
    GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'gdal312.dll')
    GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'geos_c.dll')


SECRET_KEY = config('SECRET_KEY')
TWO_GIS_API_KEY = os.getenv('TWO_GIS_API_KEY')
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
YANDEX_GEOCODE_KEY=os.getenv("YANDEX_GEOCODE_KEY")
OPENCELLID_KEY=config("OPENCELLID_KEY")

OPENAI_API_KEY=config("OPENAI_API_KEY")
OPENROUTER_API_KEY=config("OPENROUTER_API_KEY")
GOOGLE_MAP_API_KEY=config("GOOGLE_MAP_API_KEY")

OPENCELLID_RATE_LIMIT = {
    'requests_per_second': 0.5,  # 1 request every 2 seconds
    'max_requests_per_day': 10000,
}

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

DEBUG = config('DEBUG', default=False, cast=bool)


# Default map center / zoom (optional)
YANDEX_MAP_CENTER = [41.311081, 69.240562]
YANDEX_MAP_ZOOM = 12
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '45.138.159.84',
    'api.getplace.uz',
    'api.pointiq.uz',
    'pointiq.uz',
    'www.api.pointiq.uz',
]
# HTTPS va proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    'django.contrib.gis',

    # installed packages
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_simplejwt',
    'twilio',
    'celery',
    'drf_yasg',
    'hitcount',
    'corsheaders',
    "django_json_widget",
    'leaflet',



    # local apps
    'apps.users',
    'apps.dictionary',
    'apps.areas',
    'apps.shared',
    'apps.core',
    'apps.citizens',
    'apps.competitors',
    'apps.property',
    'apps.government_bodies',
    'apps.networks',
    "apps.ai",

]



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Per-user budgets for paid external APIs (see apps/shared/throttles.py).
    'DEFAULT_THROTTLE_RATES': {
        'ai': '20/hour',
        'google': '10/hour',
        'twogis': '30/hour',
        # OTP: codes sent / codes checked, per phone number.
        'otp_send': '5/hour',
        'otp_verify': '10/hour',
        'signup': '10/hour',
    },
    # Number of reverse proxies in front of gunicorn. DRF takes the client IP
    # from that position in X-Forwarded-For; unset, it trusts the whole
    # header and anyone can fake their IP to dodge IP-based throttles.
    'NUM_PROXIES': config('NUM_PROXIES', default=1, cast=int),
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header. Example: "Bearer <access_token>"',
        }
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "ON_LOGIN_SUCCESS": "rest_framework_simplejwt.serializers.default_on_login_success",
    "ON_LOGIN_FAILED": "rest_framework_simplejwt.serializers.default_on_login_failed",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (41.2995, 69.2401), # Toshkent koordinatalari
    'DEFAULT_ZOOM': 12,
    'MIN_ZOOM': 5,
    'MAX_ZOOM': 18,
    'TILES': [
        ('satellite', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '&copy; OpenStreetMap contributors'}),
        # Agar Google xaritasini xohlasangiz:
        ('Google Maps', 'http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
         {'attribution': 'Google'}),
    ],
}


ROOT_URLCONF = "get_place.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "get_place.wsgi.application"


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = '/app/staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


AUTH_USER_MODEL = 'users.User'


# Redis konfiguratsiyasi
REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)

# Shared cache: throttle counters must be shared by all gunicorn workers and
# survive restarts, which the default per-process LocMemCache does not do.
# DB 1 keeps it apart from the Celery broker on DB 0.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("CACHE_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/1"),
    }
}

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='Asia/Tashkent')

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}


ESKIZ_EMAIL = config('ESKIZ_EMAIL')
ESKIZ_PASSWORD = config('ESKIZ_PASSWORD')
