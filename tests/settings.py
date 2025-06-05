import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "django-insecure-dummy-secret-key-for-testing-!*#&@(^"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",  # Necessary because the plugin uses set_session_cookie
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",  # For token blacklist functionality
    "drf_spectacular",
    "django_cookiejwt",  # Current plugin
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # For sessions to work
    "django_cookiejwt.middlewares.RefreshTokenMiddleware",  # Current plugin
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Django Standard Authentication
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, ":memory:"),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Set your plugin's default authentication class for tests
        "django_cookiejwt.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        # Allow access for tests by default unless otherwise specified.
        # For secure endpoints, it is better to use IsAuthenticated and create users.
        "rest_framework.permissions.AllowAny",
    ),
    # Disable Browsable API for tests if it is not required
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Increased lifetime for easier debugging of tests
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "USER_ID_FIELD": "id",  # User model field for identification
    "USER_ID_CLAIM": "user_id",  # Field name in JWT token
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_OBTAIN_SERIALIZER": "django_cookiejwt.serializers.CustomTokenObtainPairSerializer",
}

# Using a fast password hasher to speed up tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Settings for drf-spectacular (to avoid unnecessary warnings in tests)
SPECTACULAR_SETTINGS = {
    "SERVE_INCLUDE_SCHEMA": False,
    "DISABLE_ERRORS_AND_WARNINGS": True,
}

# Cookie settings (plugin uses Django session cookie settings)
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = False # False for HTTP tests
# SESSION_COOKIE_SAMESITE = 'Lax'

# Template settings (may be needed for some DRF views or admin)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
