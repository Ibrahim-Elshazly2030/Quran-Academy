"""
إعدادات منظومة إدارة الأكاديمية والمدارس القرآنية (Furqan Quran Academy)
Django settings for Furqan Academy project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# مسار المشروع الرئيسي
BASE_DIR = Path(__file__).resolve().parent.parent

# تحميل متغيرات البيئة من ملف .env
load_dotenv(BASE_DIR / '.env')

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-furqan-quran-academy-platform-key-2026-secure-token')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

if ENVIRONMENT.lower() == 'production':
    DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',') if host.strip()]

if ENVIRONMENT.lower() == 'production':
    csrf_hosts = [host for host in ALLOWED_HOSTS if host not in ('localhost', '127.0.0.1', '0.0.0.0')]
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in csrf_hosts]
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8005',
        'http://127.0.0.1:8005',
        'http://0.0.0.0:8005',
    ]

SECURE_REFERRER_POLICY = 'same-origin'

# التطبيقات المثبتة
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # تطبيقات المنظومة القرآنية
    'accounts.apps.AccountsConfig',
    'academy.apps.AcademyConfig',
    'attendance.apps.AttendanceConfig',
    'evaluations.apps.EvaluationsConfig',
    'reports.apps.ReportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.academy_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# نموذج المستخدم المخصص
AUTH_USER_MODEL = 'accounts.User'

# إعدادات قاعدة البيانات: PostgreSQL كخيار أساسي و SQLite كبديل مرن
USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', 'False').lower() in ('true', '1', 't')

if USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'quran_academy_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# التحقق من قوة كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# اللغة والمنطقة الزمنية (العربية ودعم التوقيت)
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'ar')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Riyadh')
USE_I18N = True
USE_TZ = True

# الملفات الثابتة والوسائط
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# مسارات تسجيل الدخول والخروج
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard_redirect'
LOGOUT_REDIRECT_URL = 'accounts:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
