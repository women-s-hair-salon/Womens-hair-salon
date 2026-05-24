# settings_dev.py
# -------------------------------------------------------
# این فایل رو کنار settings.py پروژه‌ات قرار بده
# و در settings.py اصلی‌ات این رو به انتها اضافه کن:
#
#   if DEBUG:
#       try:
#           from .settings_dev import *
#       except ImportError:
#           pass
# -------------------------------------------------------

# امنیت HTTPS رو خاموش کن (چون در لوکال SSL نداریم)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = None

# S3 رو خاموش کن - فایل‌ها لوکال ذخیره بشن
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# لاگ روی کنسول (بجای فایل)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# CSP در تست خاموش (تا خطاهای UI بده نده)
CSP_REPORT_ONLY = True

# ایمیل روی کنسول
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'