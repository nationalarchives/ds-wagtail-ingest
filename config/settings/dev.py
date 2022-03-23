from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + [
    "django_extensions",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "#8ee3-hpaw+_enm-^20irgts6i*f88$j*cw+tnew!)6ln-94r9"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
