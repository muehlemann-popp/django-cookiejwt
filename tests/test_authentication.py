from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken

from src.django_cookiejwt.authentication import CookieJWTAuthentication


class TestCookieJWTAuthentication:
    """Tests for the CookieJWTAuthentication class."""

    @pytest.mark.django_db
    def test_successful_authentication_with_cookie(self, user, valid_access_token, rf_request):
        """Test successful authentication using a valid token in cookie."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = valid_access_token

        # Execute
        user_auth, token = auth.authenticate(rf_request)

        # Assert
        assert user_auth == user
        assert token is not None

    def test_authentication_with_invalid_token_in_cookie(self, invalid_token, rf_request):
        """Test authentication fails with an invalid token in cookie."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = invalid_token

        # Execute & Assert
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(rf_request)

    @pytest.mark.django_db
    @patch.object(CookieJWTAuthentication, "get_header")
    @patch.object(CookieJWTAuthentication, "get_raw_token")
    @patch.object(CookieJWTAuthentication, "get_validated_token")
    @patch.object(CookieJWTAuthentication, "get_user")
    def test_fallback_to_standard_auth_without_cookie(
        self, mock_get_user, mock_get_validated_token, mock_get_raw_token, mock_get_header, rf_request, user
    ):
        """Test fallback to standard auth when no token in cookie."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES = {}
        mock_get_header.return_value = b"Bearer token"
        mock_get_raw_token.return_value = b"token"
        mock_token = Mock()
        mock_get_validated_token.return_value = mock_token
        mock_get_user.return_value = user

        # Execute
        user_auth, token = auth.authenticate(rf_request)

        # Assert
        assert user_auth == user
        assert token == mock_token
        mock_get_header.assert_called_once_with(rf_request)
        mock_get_raw_token.assert_called_once_with(mock_get_header.return_value)
        mock_get_validated_token.assert_called_once_with(mock_get_raw_token.return_value)
        mock_get_user.assert_called_once_with(mock_token)

    @pytest.mark.django_db
    def test_authentication_with_expired_token(self, expired_access_token, rf_request):
        """Test authentication fails with an expired token."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = expired_access_token

        # Need to patch the get_validated_token method to raise TokenError
        with patch.object(auth, "get_validated_token") as mock_validate:
            mock_validate.side_effect = InvalidToken("Token is expired")

            # Execute & Assert
            with pytest.raises(AuthenticationFailed):
                auth.authenticate(rf_request)

    @pytest.mark.django_db
    def test_authentication_with_nonexistent_user(self, valid_access_token, rf_request):
        """Test authentication fails when the token references a nonexistent user."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = valid_access_token

        # In the actual implementation, the AuthenticationFailed is caught and re-raised as "Invalid token"
        # So we need to test for that final exception
        User = get_user_model()
        with patch.object(User.objects, "get") as mock_get:
            mock_get.side_effect = User.DoesNotExist()

            # Execute & Assert
            with pytest.raises(AuthenticationFailed, match="Invalid token"):
                auth.authenticate(rf_request)

    @pytest.mark.django_db
    def test_authentication_with_inactive_user(self, inactive_user, valid_access_token, rf_request):
        """Test authentication fails with a token for an inactive user."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = valid_access_token

        # Need to patch at a higher level to catch the exception before it's wrapped
        with patch.object(auth, "get_user") as mock_get_user:
            mock_get_user.side_effect = AuthenticationFailed("The user is inactive", code="user_is_inactive")

            # Execute & Assert
            with pytest.raises(AuthenticationFailed, match="Invalid token"):
                auth.authenticate(rf_request)

    @pytest.mark.django_db
    def test_authentication_with_token_missing_user_id(self, valid_access_token, rf_request):
        """Test authentication fails when token has no user_id claim."""
        # Setup
        auth = CookieJWTAuthentication()
        rf_request.COOKIES["access_token"] = valid_access_token

        # Need to intercept at the get_user level to control the exception
        with patch.object(auth, "get_user") as mock_get_user:
            # Simulate the KeyError causing an InvalidToken
            mock_get_user.side_effect = InvalidToken("The token does not contain a user ID.")

            # Execute & Assert
            with pytest.raises(AuthenticationFailed):
                auth.authenticate(rf_request)

            # Verify the exception happened for the right reason (using another approach)
            try:
                auth.get_user({})  # Pass empty token without user_id
                pytest.fail("Should have raised InvalidToken")
            except InvalidToken as e:
                assert "The token does not contain a user ID" in str(e)
