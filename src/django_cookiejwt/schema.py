from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "authentication.authentication.CookieJWTAuthentication"
    name = "JWT via Cookie"

    def get_security_definition(self, *args, **kwargs):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "JWT token passed via HttpOnly cookie",
        }
