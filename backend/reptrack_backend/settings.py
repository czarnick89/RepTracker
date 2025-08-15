from pathlib import Path
from decouple import config
from datetime import timedelta
from corsheaders.defaults import default_headers
import os

# ===============================
# BASE / PATHS / SECRET
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

FRONTEND_URL = config('FRONTEND_URL', default='https://localhost:5173')
FRONTEND_PROFILE_URL = config('FRONTEND_PROFILE_URL', default=f'{FRONTEND_URL}/profile')
BACKEND_URL = config('BACKEND_URL')

# ===============================
# APPLICATIONS
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'sslserver',
    'django_extensions',

    'users',
    'workouts',
]

# ===============================
# MIDDLEWARE
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===============================
# URLS & TEMPLATES
# ===============================
ROOT_URLCONF = 'reptrack_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'reptrack_backend.wsgi.application'

# ===============================
# DATABASE
# ===============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# ===============================
# AUTHENTICATION
# ===============================
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'users.backends.CaseInsensitiveEmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===============================
# REST FRAMEWORK / JWT
# ===============================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.JWTAuthenticationFromCookie',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute', 
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_COOKIE': 'access',
    'AUTH_COOKIE_REFRESH': 'refresh',
}

# ===============================
# CORS / CSRF
# ===============================
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://127.0.0.1:5173'
).split(',')

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://localhost:5173,https://127.0.0.1:5173'
).split(',')

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["cache-control"]

# ===============================
# INTERNATIONALIZATION
# ===============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===============================
# STATIC FILES
# ===============================
STATIC_URL = 'static/'

# ===============================
# DEFAULT AUTO FIELD
# ===============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================
# EMAIL
# ===============================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # change for production

# ===============================
# THIRD-PARTY API KEYS
# ===============================
EXERCISE_DB_BASE_URL = config('EXERCISE_DB_BASE_URL', default='https://exercisedb.p.rapidapi.com')
EXERCISE_DB_HOST = config('EXERCISE_DB_HOST', default='exercisedb.p.rapidapi.com')

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_SECRET')
GOOGLE_REDIRECT_URI = config(
    'GOOGLE_REDIRECT_URI',
    default='https://127.0.0.1:8000/api/v1/workouts/google-calendar/oauth2callback'
)
GOOGLE_AUTH_URI = config('GOOGLE_AUTH_URI', default='https://accounts.google.com/o/oauth2/auth')
GOOGLE_TOKEN_URI = config('GOOGLE_TOKEN_URI', default='https://oauth2.googleapis.com/token')
GOOGLE_REVOKE_URI = config('GOOGLE_REVOKE_URI', default='https://oauth2.googleapis.com/revoke')

# ===============================
# SESSIONS & SECURITY
# ===============================
SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'

SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (default)

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'