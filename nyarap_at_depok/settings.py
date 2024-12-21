from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#r8z7-fal_cfwxz88l(+7apsnmxuzsdyea+-f=g22978)i(jn_'

# SECURITY WARNING: don't run with debug turned on in production!
PRODUCTION = os.getenv("PRODUCTION", False)
DEBUG = not PRODUCTION

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "valiza-nadya-nyarapatdepok.pbp.cs.ui.ac.id", "10.0.2.2"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'main',
    'discovery',
    'nyarap_detailer',
    'nyarap_nanti',
    'reviews',
    'corsheaders',
    'authentication',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nyarap_at_depok.urls'

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

WSGI_APPLICATION = 'nyarap_at_depok.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / 'static'
    ]
else:
    STATIC_ROOT = BASE_DIR / 'static'

# Excel file path setting
if not os.getenv("PRODUCTION", False):
    EXCEL_DATA_PATH = os.path.join(BASE_DIR, 'static', 'data', 'dataset.xlsx')
else:
    EXCEL_DATA_PATH = os.path.join(STATIC_ROOT, 'data', 'dataset.xlsx')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security and Session Settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://valiza-nadya-nyarapatdepok.pbp.cs.ui.ac.id",
    "https://valiza-nadya-nyarapatdepok.pbp.cs.ui.ac.id"
]

# Authentication Settings
LOGIN_URL = 'main:login'
LOGIN_REDIRECT_URL = 'main:show_main'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://10.0.2.2:8000",
    "http://localhost:8080",  # Flutter web default port
    "http://127.0.0.1:8080",
]

# Update CSRF_TRUSTED_ORIGINS juga untuk include semua port
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://valiza-nadya-nyarapatdepok.pbp.cs.ui.ac.id",
    "https://valiza-nadya-nyarapatdepok.pbp.cs.ui.ac.id"
]

# Pastikan development settings konsisten
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    CORS_ALLOW_CREDENTIALS = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    CORS_ORIGIN_ALLOW_ALL = True 