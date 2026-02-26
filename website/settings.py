"""
HostFlow – Django Settings (Production Ready for Render)
"""

from pathlib import Path
import os
import dj_database_url

# ── BASE DIR ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ── SECURITY ────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

DEBUG = True
ALLOWED_HOSTS = ['*']


# CSRF for Render (IMPORTANT)
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']


# ── INSTALLED APPS ──────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'hostflow',
]


# ── MIDDLEWARE ──────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'hostflow.middleware.TenantIsolationMiddleware',
]


# ── URLS / WSGI ─────────────────────────────────────────
ROOT_URLCONF = 'website.urls'
WSGI_APPLICATION = 'website.wsgi.application'


# ── TEMPLATES ───────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'hostflow' / 'templates'],
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


# ── DATABASE (Render PostgreSQL) ────────────────────────
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get("DATABASE_URL")
    )
}


# ── AUTH ────────────────────────────────────────────────
AUTH_USER_MODEL = 'hostflow.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'


# ── INTERNATIONAL ───────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True


# ── STATIC FILES ────────────────────────────────────────
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    BASE_DIR / "hostflow/static"
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ── MEDIA FILES ─────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── EMAIL CONFIG (OTP - Gmail SMTP) ─────────────────────
# ── EMAIL CONFIG ─────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')

EMAIL_TIMEOUT = 5

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ── OTP SETTINGS ────────────────────────────────────────
OTP_EXPIRY_SECONDS = 300   # 5 minutes
OTP_RESEND_LIMIT = 3


# ── SESSION SETTINGS ────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour


# ── SECURITY (Render HTTPS) ─────────────────────────────
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# ── RAZORPAY ───────────────────────────────────────────
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')