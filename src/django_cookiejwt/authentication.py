from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings


class CookieJWTAuthentication(JWTAuthentication):
    default_error_messages = {
        "user_not_found": _("User not found"),
        "user_is_inactive": _("The user is inactive"),
    }

    def authenticate(self, request: Request):
        # Getting access token from cookies
        cookie_access_token = request.COOKIES.get("access_token")

        if cookie_access_token is None:
            return super().authenticate(request)

        if cookie_access_token is None:
            return None  # Token not found, consider anonymous user

        try:
            # Validating access token
            validated_token = self.get_validated_token(cookie_access_token.encode("utf-8"))
            return self.get_user(validated_token), validated_token
        except Exception:
            raise AuthenticationFailed("Invalid token")

    def get_user(self, validated_token):
        """Finds and returns a user by a validated token."""
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("The token does not contain a user ID."))

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(
                self.default_error_messages["user_not_found"],
                code="user_not_found",
            )

        if not user.is_active:
            raise AuthenticationFailed(
                self.default_error_messages["user_is_inactive"],
                code="user_is_inactive",
            )

        return user
