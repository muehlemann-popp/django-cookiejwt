from django.conf import settings

COOKIEJWT_HTTPONLY = getattr(settings, "COOKIEJWT_HTTPONLY", True)
COOKIEJWT_SECURE = getattr(settings, "COOKIEJWT_SECURE", False)  # For development; should be True in production
COOKIEJWT_SAMESITE = getattr(settings, "COOKIEJWT_SAMESITE", "Lax")

COOKIEJWT_NAME = getattr(settings, "COOKIEJWT_NAME", "sessionid")

COOKIEJWT_ACCESS_MAX_AGE = getattr(settings, "COOKIEJWT_ACCESS_MAX_AGE", 300)  # in seconds = 5 minutes
COOKIEJWT_REFRESH_MAX_AGE = getattr(settings, "COOKIEJWT_REFRESH_MAX_AGE", 86400)  # in seconds = 1 day

COOKIEJWT_PATH = getattr(settings, "COOKIEJWT_PATH", "/")
COOKIEJWT_DOMAIN = getattr(settings, "COOKIEJWT_DOMAIN", None)
