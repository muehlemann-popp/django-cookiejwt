import logging
from typing import Optional

from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CookieJWTAuthentication
from .services import set_access_token_cookie

logger = logging.getLogger(__name__)


class RefreshTokenMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest) -> None:
        if request.path.startswith("/admin/"):
            return None

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token:
            return None

        jwt_authenticator = CookieJWTAuthentication()

        try:
            validated_token = jwt_authenticator.get_validated_token(access_token.encode("utf-8"))
            request.user = jwt_authenticator.get_user(validated_token)
        except (InvalidToken, TokenError, AuthenticationFailed):
            if refresh_token:
                new_access_token_str = self.try_refresh_access_token(refresh_token)
                setattr(request, "new_access_token", new_access_token_str)

                if new_access_token_str:
                    request.COOKIES["access_token"] = new_access_token_str
                    try:
                        validated_new_token = jwt_authenticator.get_validated_token(
                            new_access_token_str.encode("utf-8")
                        )
                        request.user = jwt_authenticator.get_user(validated_new_token)
                    except (InvalidToken, TokenError, AuthenticationFailed):
                        logger.warning(
                            "New access token is invalid after refresh attempt. User remains unauthenticated."
                        )
        return None

    def process_response(self, request: WSGIRequest, response: Response) -> Response:
        new_access_token = getattr(request, "new_access_token", None)
        if new_access_token:
            set_access_token_cookie(response, new_access_token)
        return response

    @staticmethod
    def try_refresh_access_token(refresh_token: str) -> Optional[str]:
        try:
            refresh = RefreshToken(refresh_token)  # type: ignore[arg-type]
            return str(refresh.access_token)
        except (InvalidToken, TokenError):
            return None
