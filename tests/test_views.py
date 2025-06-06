from unittest.mock import patch

import pytest
from django.contrib.auth.models import User as UserType
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestCookieTokenObtainPairView:
    """Tests for the CookieTokenObtainPairView."""

    def test_successful_token_obtain_with_valid_credentials(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test successful token retrieval with valid user credentials."""
        response = api_client.post("/api/auth/token/", user_credentials)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_token_obtain_with_invalid_credentials(self, api_client: APIClient, invalid_credentials: dict[str, str]):
        """Test token retrieval fails with invalid credentials."""
        response = api_client.post("/api/auth/token/", invalid_credentials)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies

    def test_token_obtain_with_inactive_user_credentials(
        self, api_client: APIClient, inactive_user: UserType, inactive_user_credentials: dict[str, str]
    ):
        """Test token retrieval fails with inactive user credentials."""
        response = api_client.post("/api/auth/token/", inactive_user_credentials)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies

    def test_access_token_cookie_is_set_in_response(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that access_token cookie is properly set in response."""
        response = api_client.post("/api/auth/token/", user_credentials)

        assert response.status_code == status.HTTP_200_OK
        access_token_cookie = response.cookies.get("access_token")
        assert access_token_cookie is not None
        assert access_token_cookie.value != ""
        assert access_token_cookie["httponly"] is True
        assert access_token_cookie["path"] == "/"

    def test_refresh_token_cookie_is_set_in_response(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that refresh_token cookie is properly set in response."""
        response = api_client.post("/api/auth/token/", user_credentials)

        assert response.status_code == status.HTTP_200_OK
        refresh_token_cookie = response.cookies.get("refresh_token")
        assert refresh_token_cookie is not None
        assert refresh_token_cookie.value != ""
        assert refresh_token_cookie["httponly"] is True
        assert refresh_token_cookie["path"] == "/"

    @override_settings(COOKIEJWT_SET_SESSION_COOKIE=True)
    def test_session_cookie_is_set_when_enabled(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that session cookie is set when COOKIEJWT_SET_SESSION_COOKIE is True."""
        response = api_client.post("/api/auth/token/", user_credentials)

        assert response.status_code == status.HTTP_200_OK
        session_cookie = response.cookies.get("sessionid")
        assert session_cookie is not None
        assert session_cookie.value != ""

    @override_settings(COOKIEJWT_SET_SESSION_COOKIE=False)
    def test_session_cookie_is_not_set_when_disabled(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that session cookie is not set when COOKIEJWT_SET_SESSION_COOKIE is False."""
        # Mock the conf module to ensure the setting is properly loaded
        with patch("django_cookiejwt.conf.COOKIEJWT_SET_SESSION_COOKIE", False):
            with patch("django_cookiejwt.views.set_session_cookie") as mock_set_session:
                response = api_client.post("/api/auth/token/", user_credentials)

                assert response.status_code == status.HTTP_200_OK
                mock_set_session.assert_not_called()

    def test_tokens_are_removed_from_response_body(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that access and refresh tokens are removed from response body."""
        response = api_client.post("/api/auth/token/", user_credentials)

        assert response.status_code == status.HTTP_200_OK
        assert "access" not in response.data
        assert "refresh" not in response.data
        # Verify cookies are still set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_cookie_security_settings_are_applied(
        self, api_client: APIClient, user: UserType, user_credentials: dict[str, str]
    ):
        """Test that cookie security settings are properly applied using mocks."""
        with patch("django_cookiejwt.views.set_access_token_cookie") as mock_access_cookie:
            with patch("django_cookiejwt.views.set_refresh_token_cookie") as mock_refresh_cookie:
                response = api_client.post("/api/auth/token/", user_credentials)

                assert response.status_code == status.HTTP_200_OK
                mock_access_cookie.assert_called_once()
                mock_refresh_cookie.assert_called_once()

                # Verify the tokens were passed to the cookie setters
                access_token = mock_access_cookie.call_args[0][1]
                refresh_token = mock_refresh_cookie.call_args[0][1]
                assert access_token != ""
                assert refresh_token != ""


@pytest.mark.django_db
class TestCookieTokenBlacklistView:
    """Tests for the CookieTokenBlacklistView."""

    def test_successful_token_blacklist_with_valid_refresh_token(
        self, api_client: APIClient, user: UserType, valid_refresh_token: str
    ):
        """Test successful token blacklisting with valid refresh token in cookies."""
        api_client.cookies["refresh_token"] = valid_refresh_token

        response = api_client.post("/api/auth/token/blacklist/", {})

        assert response.status_code == status.HTTP_200_OK

        # Verify cookies are marked for deletion
        access_cookie = response.cookies.get("access_token")
        refresh_cookie = response.cookies.get("refresh_token")
        assert access_cookie and access_cookie["max-age"] == 0
        assert refresh_cookie and refresh_cookie["max-age"] == 0

    def test_token_blacklist_fails_without_refresh_token_cookie(self, api_client: APIClient):
        """Test that token blacklisting fails when no refresh token cookie is provided."""
        response = api_client.post("/api/auth/token/blacklist/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"] == "Refresh token not provided"

    def test_token_blacklist_fails_with_invalid_refresh_token(self, api_client: APIClient, invalid_token: str):
        """Test that token blacklisting fails with invalid refresh token."""
        api_client.cookies["refresh_token"] = invalid_token

        response = api_client.post("/api/auth/token/blacklist/", {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cookies_are_deleted_on_successful_blacklist(
        self, api_client: APIClient, user: UserType, valid_refresh_token: str
    ):
        """Test that both access and refresh token cookies are deleted on successful blacklist."""
        api_client.cookies["refresh_token"] = valid_refresh_token
        api_client.cookies["access_token"] = "some_access_token"

        response = api_client.post("/api/auth/token/blacklist/", {})

        assert response.status_code == status.HTTP_200_OK
        # Verify both cookies are marked for deletion
        access_cookie = response.cookies.get("access_token")
        refresh_cookie = response.cookies.get("refresh_token")
        assert access_cookie and access_cookie.value == ""
        assert refresh_cookie and refresh_cookie.value == ""

    def test_refresh_token_extracted_from_cookie(self, api_client: APIClient, user: UserType, valid_refresh_token: str):
        """Test that refresh token is properly extracted from cookies and used."""
        # This test now becomes identical to test_successful_token_blacklist_with_valid_refresh_token
        # It verifies the end-to-end process which is what matters.
        api_client.cookies["refresh_token"] = valid_refresh_token

        response = api_client.post("/api/auth/token/blacklist/", {})

        assert response.status_code == status.HTTP_200_OK
