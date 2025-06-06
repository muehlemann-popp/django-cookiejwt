from datetime import timedelta
from typing import Any
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory
from freezegun import freeze_time as _freeze_time
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


@pytest.fixture
def user() -> UserType:
    """Create an active user for testing."""
    return User.objects.create_user(
        username="testuser", email="testuser@example.com", password="testpassword123", is_active=True
    )


@pytest.fixture
def inactive_user() -> UserType:
    """Create an inactive user for testing."""
    return User.objects.create_user(
        username="inactiveuser", email="inactiveuser@example.com", password="testpassword123", is_active=False
    )


@pytest.fixture
def valid_access_token(user: UserType) -> str:
    """Generate a valid access token for the test user."""
    token = AccessToken.for_user(user)
    return str(token)


@pytest.fixture
def expired_access_token(user: UserType) -> str:
    """Generate an expired access token for the test user."""
    # Patch the api_settings object where it's looked up by the token classes
    with patch("rest_framework_simplejwt.tokens.api_settings.ACCESS_TOKEN_LIFETIME", timedelta(seconds=-1)):
        token = AccessToken.for_user(user)
        return str(token)


@pytest.fixture
def valid_refresh_token(user: UserType) -> str:
    """Generate a valid refresh token for the test user."""
    token = RefreshToken.for_user(user)
    return str(token)


@pytest.fixture
def expired_refresh_token(user: UserType) -> str:
    """Generate an expired refresh token for the test user."""
    # Patch the api_settings object where it's looked up by the token classes
    with patch("rest_framework_simplejwt.tokens.api_settings.REFRESH_TOKEN_LIFETIME", timedelta(seconds=-1)):
        token = RefreshToken.for_user(user)
        return str(token)


@pytest.fixture
def invalid_token() -> str:
    """Generate a malformed/invalid token string."""
    return "invalid.jwt.token.string"


@pytest.fixture
def user_credentials() -> dict[str, str]:
    """Return valid user credentials for login testing."""
    return {"username": "testuser", "password": "testpassword123"}


@pytest.fixture
def inactive_user_credentials() -> dict[str, str]:
    """Return credentials for inactive user."""
    return {"username": "inactiveuser", "password": "testpassword123"}


@pytest.fixture
def invalid_credentials() -> dict[str, str]:
    """Return invalid credentials for testing failed authentication."""
    return {"username": "wronguser", "password": "wrongpassword"}


@pytest.fixture
def request_with_cookies(valid_access_token: str, valid_refresh_token: str) -> WSGIRequest:
    """Create a request with access_token and refresh_token cookies set."""
    factory = RequestFactory()
    request = factory.get("/")
    request.COOKIES = {
        "access_token": valid_access_token,
        "refresh_token": valid_refresh_token,
    }
    return request


@pytest.fixture
def request_without_cookies() -> WSGIRequest:
    """Create a request without any cookies."""
    factory = RequestFactory()
    request = factory.get("/")
    request.COOKIES = {}
    return request


@pytest.fixture
def mock_response() -> Mock:
    """Create a mock Response object for testing cookie operations."""
    response = Mock(spec=Response)
    response.data = {}
    response.set_cookie = Mock()
    return response


@pytest.fixture
def cookie_settings() -> dict[str, Any]:
    """Return default cookie settings for testing."""
    return {
        "COOKIEJWT_HTTPONLY": True,
        "COOKIEJWT_SECURE": False,
        "COOKIEJWT_SAMESITE": "Lax",
        "COOKIEJWT_ACCESS_MAX_AGE": 300,
        "COOKIEJWT_REFRESH_MAX_AGE": 86400,
        "COOKIEJWT_PATH": "/",
        "COOKIEJWT_DOMAIN": None,
        "COOKIEJWT_SET_SESSION_COOKIE": True,
    }


@pytest.fixture
def secure_cookie_settings() -> dict[str, Any]:
    """Return secure cookie settings for production testing."""
    return {
        "COOKIEJWT_HTTPONLY": True,
        "COOKIEJWT_SECURE": True,
        "COOKIEJWT_SAMESITE": "Strict",
        "COOKIEJWT_ACCESS_MAX_AGE": 300,
        "COOKIEJWT_REFRESH_MAX_AGE": 86400,
        "COOKIEJWT_PATH": "/",
        "COOKIEJWT_DOMAIN": "example.com",
        "COOKIEJWT_SET_SESSION_COOKIE": True,
    }


@pytest.fixture
def insecure_cookie_settings() -> dict[str, Any]:
    """Return insecure cookie settings for testing edge cases."""
    return {
        "COOKIEJWT_HTTPONLY": False,
        "COOKIEJWT_SECURE": False,
        "COOKIEJWT_SAMESITE": None,
        "COOKIEJWT_ACCESS_MAX_AGE": 300,
        "COOKIEJWT_REFRESH_MAX_AGE": 86400,
        "COOKIEJWT_PATH": "/",
        "COOKIEJWT_DOMAIN": None,
        "COOKIEJWT_SET_SESSION_COOKIE": False,
    }


@pytest.fixture
def short_expiry_cookie_settings() -> dict[str, Any]:
    """Return cookie settings with short expiry times for testing."""
    return {
        "COOKIEJWT_HTTPONLY": True,
        "COOKIEJWT_SECURE": False,
        "COOKIEJWT_SAMESITE": "Lax",
        "COOKIEJWT_ACCESS_MAX_AGE": 5,
        "COOKIEJWT_REFRESH_MAX_AGE": 60,
        "COOKIEJWT_PATH": "/",
        "COOKIEJWT_DOMAIN": None,
        "COOKIEJWT_SET_SESSION_COOKIE": True,
    }


@pytest.fixture
def jwt_settings() -> dict[str, Any]:
    """Return default JWT settings for testing."""
    return {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
        "ROTATE_REFRESH_TOKENS": False,
        "BLACKLIST_AFTER_ROTATION": True,
        "UPDATE_LAST_LOGIN": False,
        "ALGORITHM": "HS256",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
    }


@pytest.fixture
def short_lifetime_jwt_settings() -> dict[str, Any]:
    """Return JWT settings with short token lifetimes for testing."""
    return {
        "ACCESS_TOKEN_LIFETIME": timedelta(seconds=30),
        "REFRESH_TOKEN_LIFETIME": timedelta(minutes=5),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
        "UPDATE_LAST_LOGIN": False,
        "ALGORITHM": "HS256",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
    }


@pytest.fixture
def rotating_jwt_settings() -> dict[str, Any]:
    """Return JWT settings with token rotation enabled for testing."""
    return {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
        "REFRESH_TOKEN_LIFETIME": timedelta(hours=12),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
        "UPDATE_LAST_LOGIN": True,
        "ALGORITHM": "HS256",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
    }


@pytest.fixture
def rf_request() -> Request:
    """Create a DRF Request object for testing."""
    factory = RequestFactory()
    django_request = factory.get("/")
    return Request(django_request)


@pytest.fixture
def authenticated_request(user: UserType) -> Request:
    """Create an authenticated DRF Request object."""
    factory = RequestFactory()
    django_request = factory.get("/")
    django_request.user = user
    return Request(django_request)


@pytest.fixture
def api_client() -> APIClient:
    """Create an API client for testing endpoints."""
    return APIClient()


@pytest.fixture
def freeze_time():
    """Freeze time at a specific datetime for consistent token testing."""
    with _freeze_time("2024-01-01 12:00:00") as frozen_time:
        yield frozen_time


@pytest.fixture
def mock_session() -> Mock:
    """Create a mock Django session object."""
    session = Mock()
    session.session_key = "test_session_key_123"
    session.create = Mock()
    session.save = Mock()
    return session
