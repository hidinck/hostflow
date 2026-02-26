"""
HostFlow – Django Settings (Production Ready for OTP)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ── SECURITY ─────────────────────────────────────────────
SECRET_KEY = 'django-insecure-hostflow-change-this-in-production-abc123xyz'

DEBUG = True

ALLOWED_HOSTS = ['*']


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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'hostflow.middleware.TenantIsolationMiddleware',
]


ROOT_URLCONF = 'website.urls'


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


WSGI_APPLICATION = 'website.wsgi.application'


# ── DATABASE ────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hostflow_db',
        'USER': 'postgres',
        'PASSWORD': 'Hidin@123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
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


# ── STATIC & MEDIA ──────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "hostflow/static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── EMAIL CONFIG (REAL OTP - GMAIL) ─────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ⚠️ REPLACE THESE
EMAIL_HOST_USER = 'hostfloww@gmail.com'
EMAIL_HOST_PASSWORD = 'vgdvejxeppjblsza'

# DEFAULT FROM EMAIL
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ── OTP SETTINGS (NEW) ──────────────────────────────────
OTP_EXPIRY_SECONDS = 300   # 5 minutes
OTP_RESEND_LIMIT = 3       # max resend attempts


# ── SESSION SETTINGS (FOR OTP STORAGE) ──────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour


# ── RAZORPAY ───────────────────────────────────────────
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET'

