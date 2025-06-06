from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.test import RequestFactory, override_settings
from rest_framework.response import Response

from django_cookiejwt import conf as cookiejwt_conf  # type: ignore[import]
from django_cookiejwt.services import (  # type: ignore[import]
    set_access_token_cookie,
    set_refresh_token_cookie,
    set_session_cookie,
    set_token_cookie,
)


class TestSetTokenCookie:
    """Tests for the set_token_cookie function."""

    def test_set_token_cookie_with_correct_parameters(self, mock_response: Mock):
        """Test that set_token_cookie sets cookies with correct parameters."""
        token = "test_token_value"
        key = "test_cookie_name"

        set_token_cookie(mock_response, key, token)

        mock_response.set_cookie.assert_called_once_with(
            key=key,
            value=token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=None,
            path="/",
            domain=None,
        )

    def test_set_token_cookie_with_custom_settings(self, mock_response: Mock):
        """Test that set_token_cookie respects custom Django settings."""
        token = "test_token_value"
        key = "test_cookie_name"

        cookiejwt_conf.COOKIEJWT_HTTPONLY = False
        cookiejwt_conf.COOKIEJWT_SECURE = True
        cookiejwt_conf.COOKIEJWT_SAMESITE = "Strict"
        cookiejwt_conf.COOKIEJWT_PATH = "/api/"
        cookiejwt_conf.COOKIEJWT_DOMAIN = "example.com"

        set_token_cookie(mock_response, key, token)

        mock_response.set_cookie.assert_called_once_with(
            key=key,
            value=token,
            httponly=False,
            secure=True,
            samesite="Strict",
            max_age=None,
            path="/api/",
            domain="example.com",
        )

    def test_set_token_cookie_with_delete_true(self, mock_response: Mock):
        """Test that set_token_cookie deletes cookie when delete=True."""
        token = "test_token_value"
        key = "test_cookie_name"

        cookiejwt_conf.COOKIEJWT_HTTPONLY = True
        cookiejwt_conf.COOKIEJWT_SECURE = False
        cookiejwt_conf.COOKIEJWT_SAMESITE = "Lax"
        cookiejwt_conf.COOKIEJWT_PATH = "/"
        cookiejwt_conf.COOKIEJWT_DOMAIN = None

        set_token_cookie(mock_response, key, token, delete=True)

        mock_response.set_cookie.assert_called_once_with(
            key=key,
            value="",
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=0,
            path="/",
            domain=None,
        )

    def test_set_token_cookie_with_empty_token(self, mock_response: Mock):
        """Test that set_token_cookie handles empty token string."""
        token = ""
        key = "test_cookie_name"

        cookiejwt_conf.COOKIEJWT_HTTPONLY = True
        cookiejwt_conf.COOKIEJWT_SECURE = False
        cookiejwt_conf.COOKIEJWT_SAMESITE = "Lax"
        cookiejwt_conf.COOKIEJWT_PATH = "/"
        cookiejwt_conf.COOKIEJWT_DOMAIN = None

        set_token_cookie(mock_response, key, token)

        mock_response.set_cookie.assert_called_once_with(
            key=key,
            value="",
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=None,
            path="/",
            domain=None,
        )


class TestSetAccessTokenCookie:
    """Tests for the set_access_token_cookie function."""

    @patch("django_cookiejwt.services.set_token_cookie")
    def test_set_access_token_cookie_calls_set_token_cookie(self, mock_set_token: Mock, mock_response: Mock):
        """Test that set_access_token_cookie calls set_token_cookie with correct parameters."""
        access_token = "test_access_token"

        set_access_token_cookie(mock_response, access_token)

        mock_set_token.assert_called_once_with(mock_response, "access_token", access_token, delete=False)

    @patch("django_cookiejwt.services.set_token_cookie")
    def test_set_access_token_cookie_with_delete_true(self, mock_set_token: Mock, mock_response: Mock):
        """Test that set_access_token_cookie passes delete parameter correctly."""
        access_token = "test_access_token"

        set_access_token_cookie(mock_response, access_token, delete=True)

        mock_set_token.assert_called_once_with(mock_response, "access_token", access_token, delete=True)


class TestSetRefreshTokenCookie:
    """Tests for the set_refresh_token_cookie function."""

    @patch("django_cookiejwt.services.set_token_cookie")
    def test_set_refresh_token_cookie_calls_set_token_cookie(self, mock_set_token: Mock, mock_response: Mock):
        """Test that set_refresh_token_cookie calls set_token_cookie with correct parameters."""
        refresh_token = "test_refresh_token"

        set_refresh_token_cookie(mock_response, refresh_token)

        mock_set_token.assert_called_once_with(mock_response, "refresh_token", refresh_token, delete=False)

    @patch("django_cookiejwt.services.set_token_cookie")
    def test_set_refresh_token_cookie_with_delete_true(self, mock_set_token: Mock, mock_response: Mock):
        """Test that set_refresh_token_cookie passes delete parameter correctly."""
        refresh_token = "test_refresh_token"

        set_refresh_token_cookie(mock_response, refresh_token, delete=True)

        mock_set_token.assert_called_once_with(mock_response, "refresh_token", refresh_token, delete=True)


@pytest.mark.django_db
class TestSetSessionCookie:
    """Tests for the set_session_cookie function."""

    def test_set_session_cookie_creates_new_session(self, mock_session: Mock):
        """Test that set_session_cookie creates a new session when none exists."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = mock_session
        request.session.session_key = None
        response = Response()

        mock_session.create.return_value = None

        with patch.object(response, "set_cookie"):
            set_session_cookie(response, request)

            mock_session.create.assert_called_once()

    def test_set_session_cookie_with_existing_session(self, mock_session: Mock):
        """Test that set_session_cookie uses existing session when available."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = mock_session
        request.session.session_key = "existing_session_key_456"
        response = Response()

        with patch.object(response, "set_cookie") as mock_set_cookie:
            set_session_cookie(response, request)

            mock_session.create.assert_not_called()
            mock_session.save.assert_called_once()
            mock_set_cookie.assert_called_once_with(
                key=settings.SESSION_COOKIE_NAME,
                value="existing_session_key_456",
                max_age=settings.SESSION_COOKIE_AGE,
                expires=None,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )

    def test_set_session_cookie_handles_none_session_key_after_create(self, mock_session: Mock):
        """Test that set_session_cookie handles case when session_key is None after create."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = mock_session
        request.session.session_key = None
        response = Response()

        # Simulate create() not setting session_key (edge case)
        mock_session.create.return_value = None

        with patch.object(response, "set_cookie") as mock_set_cookie:
            set_session_cookie(response, request)

            mock_session.create.assert_called_once()
            mock_session.save.assert_called_once()
            mock_set_cookie.assert_not_called()

    @override_settings(
        SESSION_COOKIE_NAME="custom_session",
        SESSION_COOKIE_AGE=7200,
        SESSION_COOKIE_PATH="/custom/",
        SESSION_COOKIE_DOMAIN="custom.example.com",
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=False,
        SESSION_COOKIE_SAMESITE="None",
    )
    def test_set_session_cookie_respects_django_session_settings(self, mock_session: Mock):
        """Test that set_session_cookie uses Django session settings."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = mock_session
        request.session.session_key = "test_session_key"
        response = Response()

        with patch.object(response, "set_cookie") as mock_set_cookie:
            set_session_cookie(response, request)

            mock_set_cookie.assert_called_once_with(
                key="custom_session",
                value="test_session_key",
                max_age=7200,
                expires=None,
                path="/custom/",
                domain="custom.example.com",
                secure=True,
                httponly=False,
                samesite="None",
            )

    def test_set_session_cookie_always_saves_session(self, mock_session: Mock):
        """Test that set_session_cookie always calls session.save()."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = mock_session
        request.session.session_key = "existing_key"
        response = Response()

        with patch.object(response, "set_cookie"):
            set_session_cookie(response, request)

            mock_session.save.assert_called_once()
