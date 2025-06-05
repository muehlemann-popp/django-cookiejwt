from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User as UserType
from django.test import RequestFactory
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from django_cookiejwt.middlewares import RefreshTokenMiddleware  # type: ignore[import]


@pytest.mark.django_db
class TestRefreshTokenMiddleware:
    """Tests for the RefreshTokenMiddleware."""

    def setup_method(self):
        """Setup for each test method."""
        self.middleware = RefreshTokenMiddleware(Mock())
        self.factory = RequestFactory()

    def test_skip_processing_for_admin_path(self):
        """Test that the middleware skips processing for /admin/ paths."""
        request = self.factory.get("/admin/")
        request.COOKIES = {"access_token": "some_token"}
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert isinstance(request.user, AnonymousUser)
        assert not hasattr(request, "new_access_token")

    def test_process_request_without_access_token(self):
        """Test that the middleware does nothing if no access token is present."""
        request = self.factory.get("/")
        request.COOKIES = {}
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert isinstance(request.user, AnonymousUser)
        assert not hasattr(request, "new_access_token")

    def test_process_with_valid_access_token(self, user: UserType, valid_access_token: str):
        """Test that the user is authenticated if a valid access token is present."""
        request = self.factory.get("/")
        request.COOKIES = {"access_token": valid_access_token}
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert request.user == user
        assert not hasattr(request, "new_access_token")

    def test_refresh_expired_access_token_with_valid_refresh_token(self, user: UserType, valid_refresh_token: str):
        """Test successful token refresh when access token is expired but refresh token is valid."""
        # Create an invalid access token that will fail validation
        invalid_access_token = "invalid.token.that.will.fail"

        request = self.factory.get("/")
        request.COOKIES = {
            "access_token": invalid_access_token,
            "refresh_token": valid_refresh_token,
        }
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert request.user == user
        assert hasattr(request, "new_access_token")
        assert request.new_access_token is not None

    def test_handle_invalid_refresh_token_on_refresh_attempt(self, user: UserType):
        """Test that refresh fails if the refresh token is invalid or expired."""
        # Use invalid tokens
        invalid_access_token = "invalid.access.token"
        invalid_refresh_token = "invalid.refresh.token"

        request = self.factory.get("/")
        request.COOKIES = {
            "access_token": invalid_access_token,
            "refresh_token": invalid_refresh_token,
        }
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert isinstance(request.user, AnonymousUser)
        assert getattr(request, "new_access_token", None) is None

    def test_handle_missing_refresh_token_on_expired_access_token(self):
        """Test user remains unauthenticated if access token is expired and no refresh token is provided."""
        # Use invalid access token
        invalid_access_token = "invalid.access.token"

        request = self.factory.get("/")
        request.COOKIES = {"access_token": invalid_access_token}
        request.user = AnonymousUser()

        self.middleware.process_request(request)

        assert isinstance(request.user, AnonymousUser)
        assert not hasattr(request, "new_access_token")

    @patch("django_cookiejwt.middlewares.set_access_token_cookie")
    def test_set_new_access_token_in_response(self, mock_set_cookie: Mock):
        """Test that a new access token is set in the response cookies if it was refreshed."""
        request = self.factory.get("/")
        new_token = "new_refreshed_access_token_string"
        setattr(request, "new_access_token", new_token)
        response = Response()

        processed_response = self.middleware.process_response(request, response)

        mock_set_cookie.assert_called_once_with(response, new_token)
        assert processed_response is response

    def test_exception_handling_during_token_validation_triggers_refresh(
        self, user: UserType, valid_refresh_token: str
    ):
        """Test that exceptions during initial token validation trigger a refresh attempt."""
        request = self.factory.get("/")
        request.COOKIES = {
            "access_token": "a_token_that_will_fail_validation",
            "refresh_token": valid_refresh_token,
        }
        request.user = AnonymousUser()

        # Create a valid token object to be returned by the mock on the second call
        new_valid_token_obj = AccessToken()
        new_valid_token_obj[api_settings.USER_ID_CLAIM] = user.id

        with patch("django_cookiejwt.authentication.CookieJWTAuthentication.get_validated_token") as mock_validate:
            # First call raises error, second call (for the new token) returns a valid object
            mock_validate.side_effect = [
                InvalidToken("Token is invalid for testing purposes"),
                new_valid_token_obj,
            ]

            self.middleware.process_request(request)

            # Assert that refresh logic was successful despite initial failure
            assert request.user == user
            assert hasattr(request, "new_access_token")
            assert request.new_access_token is not None

    @patch("django_cookiejwt.middlewares.logger")
    def test_authentication_fails_if_refreshed_token_is_also_invalid(
        self, mock_logger: Mock, user: UserType, valid_refresh_token: str
    ):
        """
        Tests the scenario where the access_token has expired, the refresh_token is valid, but the generated new
        access_token is also invalid for some reason. In this case, the user should remain unauthenticated,
        and a warning should be written to the log.
        """
        # Setting up a request with an invalid access token and a valid refresh
        request = self.factory.get("/")
        request.COOKIES = {
            "access_token": "some-invalid-or-expired-token",
            "refresh_token": valid_refresh_token,
        }
        request.user = AnonymousUser()

        # Mock the token validator so that it always throws an exception.
        # This will make it fail on the first, old token (to trigger the update logic), and then fail on the second,
        # newly created token.
        with patch("django_cookiejwt.authentication.CookieJWTAuthentication.get_validated_token") as mock_validate:
            mock_validate.side_effect = InvalidToken("Simulated token validation failure")

            # Execute the method under test
            self.middleware.process_request(request)

        assert isinstance(request.user, AnonymousUser)

        # Verify that a new token has been generated (but not validated)
        assert hasattr(request, "new_access_token")
        assert request.new_access_token is not None

        mock_logger.warning.assert_called_once_with(
            "New access token is invalid after refresh attempt. User remains unauthenticated."
        )
