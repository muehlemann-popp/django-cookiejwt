from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response

from . import conf


def set_token_cookie(response: Response, key: str, token: str, delete: bool = False) -> None:
    cookie_params = {
        "key": key,
        "value": "" if delete else token,
        "httponly": conf.COOKIEJWT_HTTPONLY,
        "secure": conf.COOKIEJWT_SECURE,
        "samesite": conf.COOKIEJWT_SAMESITE,
    }

    if delete:
        cookie_params["max_age"] = 0

    response.set_cookie(**cookie_params)


def set_access_token_cookie(response: Response, access_token: str, delete: bool = False) -> None:
    set_token_cookie(response, "access_token", access_token, delete=delete)


def set_refresh_token_cookie(response: Response, refresh_token: str, delete: bool = False) -> None:
    set_token_cookie(response, "refresh_token", refresh_token, delete=delete)


def set_session_cookie(response: Response, request: Request) -> None:
    """
    creates a session and sets the session cookie for the given response

    args:
        response: response object to set cookie on
        request: request object to get or create session
    """
    # ensure session is created and has a session key
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    # set django session cookie with proper security settings
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        max_age=settings.SESSION_COOKIE_AGE,
        expires=None,
        path=settings.SESSION_COOKIE_PATH,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )

    # make sure session is saved
    request.session.save()
