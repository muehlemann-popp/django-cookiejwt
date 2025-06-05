"""
Django Cookie JWT - JWT authentication using HTTP-only cookies for Django REST Framework
"""

__version__ = "0.0.1"
__author__ = "Andrey Kalashnikov"
__email__ = "andrey.kalashnikov@muehlemann-popp.ch"

default_app_config = "django_cookiejwt.apps.DjangoCookieJWTConfig"

from .authentication import CookieJWTAuthentication
from .middlewares import RefreshTokenMiddleware
from .views import CookieTokenBlacklistView, CookieTokenObtainPairView

__all__ = [
    "CookieJWTAuthentication",
    "RefreshTokenMiddleware",
    "CookieTokenObtainPairView",
    "CookieTokenBlacklistView",
]
