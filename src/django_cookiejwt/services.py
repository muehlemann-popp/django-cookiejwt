from rest_framework.response import Response

from .conf import (
    COOKIEJWT_ACCESS_MAX_AGE,
    COOKIEJWT_DOMAIN,
    COOKIEJWT_HTTPONLY,
    COOKIEJWT_NAME,
    COOKIEJWT_PATH,
    COOKIEJWT_SAMESITE,
    COOKIEJWT_SECURE,
)


def set_token_cookie(response: Response, key: str, token: str, delete: bool = False) -> None:
    cookie_params = {
        "key": key,
        "value": "" if delete else token,
        "httponly": COOKIEJWT_HTTPONLY,
        "secure": COOKIEJWT_SECURE,
        "samesite": COOKIEJWT_SAMESITE,
    }

    if delete:
        cookie_params["max_age"] = 0

    response.set_cookie(**cookie_params)


def set_access_token_cookie(response, access_token: str, delete: bool = False) -> None:
    set_token_cookie(response, "access_token", access_token, delete=delete)


def set_refresh_token_cookie(response, refresh_token: str, delete: bool = False) -> None:
    set_token_cookie(response, "refresh_token", refresh_token, delete=delete)


def set_session_cookie(response, request) -> None:
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

    # set session cookie with proper security settings
    response.set_cookie(
        key=COOKIEJWT_NAME,
        value=session_id,
        max_age=COOKIEJWT_ACCESS_MAX_AGE,
        expires=None,
        path=COOKIEJWT_PATH,
        domain=COOKIEJWT_DOMAIN,
        secure=COOKIEJWT_SECURE,
        httponly=COOKIEJWT_HTTPONLY,
        samesite=COOKIEJWT_SAMESITE,
    )

    # make sure session is saved
    request.session.save()
