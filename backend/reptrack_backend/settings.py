from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers
import os
from dotenv import load_dotenv
load_dotenv()

# ===============================
# BASE / PATHS / SECRET
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-me-with-a-secure-key')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ===============================
# URLs & Hosts
# ===============================
if DEBUG:
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://localhost:5173')
    BACKEND_URL = os.environ.get('BACKEND_URL', 'https://127.0.0.1:8000')
else:
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://reptracker.duckdns.org')
    BACKEND_URL = os.environ.get('BACKEND_URL', 'https://reptracker.duckdns.org')



ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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
    # App specific
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
        'NAME': os.environ.get('DB_NAME', 'reptrack_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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
if DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "https://localhost:5173",
        "https://127.0.0.1:5173",
    ]
    CORS_ALLOWED_ORIGINS = [
        "https://localhost:5173",
        "https://127.0.0.1:5173",
    ]
else:
    # Production: read from environment
    CSRF_TRUSTED_ORIGINS = os.environ.get(
        'CSRF_TRUSTED_ORIGINS', 'https://reptracker.duckdns.org'
    ).split(',')
    CORS_ALLOWED_ORIGINS = os.environ.get(
        'CORS_ALLOWED_ORIGINS', 'https://reptracker.duckdns.org'
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
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('APP_EMAIL')
    EMAIL_HOST_PASSWORD = os.environ.get('APP_EMAIL_PW')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===============================
# THIRD-PARTY API KEYS
# ===============================
EXERCISE_DB_BASE_URL = os.environ.get('EXERCISE_DB_BASE_URL', 'https://exercisedb.p.rapidapi.com')
EXERCISE_DB_HOST = os.environ.get('EXERCISE_DB_HOST', 'exercisedb.p.rapidapi.com')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get(
    'GOOGLE_REDIRECT_URI', f'{BACKEND_URL}/api/v1/workouts/google-calendar/oauth2callback'
)
GOOGLE_AUTH_URI = os.environ.get('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
GOOGLE_TOKEN_URI = os.environ.get('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
GOOGLE_REVOKE_URI = os.environ.get('GOOGLE_REVOKE_URI', 'https://oauth2.googleapis.com/revoke')

# ===============================
# SESSIONS & SECURITY
# ===============================
SESSION_ENGINE = "django.contrib.sessions.backends.db"

if DEBUG:
    # Dev: self-signed cert, no HSTS, still HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'
    SECURE_SSL_REDIRECT = False  
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    # Production: full security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 1209600  # 2 weeks
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
