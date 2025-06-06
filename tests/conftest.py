from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType
from django.utils import timezone
from rest_framework_simplejwt.settings import api_settings
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
    with patch.object(api_settings, "ACCESS_TOKEN_LIFETIME", timedelta(seconds=-1)):
        token = AccessToken.for_user(user)
        # Manually set token to be expired
        token.set_exp(claim="exp", from_time=timezone.now() - timedelta(minutes=10))
        return str(token)


@pytest.fixture
def valid_refresh_token(user: UserType) -> str:
    """Generate a valid refresh token for the test user."""
    token = RefreshToken.for_user(user)
    return str(token)


@pytest.fixture
def expired_refresh_token(user: UserType) -> str:
    """Generate an expired refresh token for the test user."""
    with patch.object(api_settings, "REFRESH_TOKEN_LIFETIME", timedelta(seconds=-1)):
        token = RefreshToken.for_user(user)
        # Manually set token to be expired
        token.set_exp(claim="exp", from_time=timezone.now() - timedelta(days=2))
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
