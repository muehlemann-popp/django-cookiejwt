from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.authentication import CookieJWTAuthentication
from authentication.services import set_access_token_cookie


class RefreshTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Eliminate requests to the Django admin panel
        if request.path.startswith("/admin/"):
            return None

        # Getting tokens from cookies
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token:
            return None  # No access token, let's skip the request

        jwt_authenticator = CookieJWTAuthentication()

        try:
            # Validating access token
            validated_token = jwt_authenticator.get_validated_token(access_token)
            request.user = jwt_authenticator.get_user(validated_token)
        except (InvalidToken, TokenError):
            # If the access token is invalid, we try to update it using refresh token
            if refresh_token:
                new_access_token = self.try_refresh_access_token(refresh_token)
                request.COOKIES["access_token"] = new_access_token
                request.new_access_token = new_access_token

    def process_response(self, request, response):
        # If a new access token was generated, we set it in cookies
        new_access_token = getattr(request, "new_access_token", None)
        if new_access_token:
            set_access_token_cookie(response, new_access_token)

        return response

    @staticmethod
    def try_refresh_access_token(refresh_token):
        """Attempts to update the access token using the refresh token."""
        try:
            refresh = RefreshToken(refresh_token)
            return str(refresh.access_token)
        except (InvalidToken, TokenError):
            return None  # If the refresh token is invalid, return None
