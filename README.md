# Django Cookie JWT

[![codecov](https://codecov.io/gh/muehlemann-popp/django-cookiejwt/graph/badge.svg?token=XR33TARA8C)](https://codecov.io/gh/muehlemann-popp/django-cookiejwt)
![Mypy Checked](https://img.shields.io/badge/checked%20with-mypy-blue.svg)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![PyPI version](https://img.shields.io/pypi/v/django-cookiejwt.svg)](https://pypi.org/project/django-cookiejwt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

JWT authentication using HTTP-only cookies for Django REST Framework.

## Overview

This plugin provides secure JWT authentication by storing tokens in HTTP-only cookies instead of local storage or headers. This approach reduces XSS risks and simplifies frontend authentication handling.

## Features

- **HTTP-only cookies**: Tokens stored securely in browser cookies
- **Automatic token refresh**: Middleware handles token renewal transparently
- **Fallback authentication**: Supports both cookie and header-based authentication
- **Session cookie support**: Optional Django session cookie creation
- **OpenAPI integration**: Automatic API documentation with drf-spectacular
- **Customizable settings**: Flexible cookie configuration options

## Installation

```bash
pip install django-cookiejwt
```

## Quick Setup

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_cookiejwt',
]
```

2. Add middleware:

```python
MIDDLEWARE = [
    # ... other middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_cookiejwt.middlewares.RefreshTokenMiddleware',
    # ... other middleware
]
```

3. Configure authentication:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'django_cookiejwt.authentication.CookieJWTAuthentication',
    ],
}
```

4. Include URLs:

```python
from django.urls import path, include

urlpatterns = [
    # ... your urls
    path('api/auth/', include('django_cookiejwt.urls')),
]
```

## Configuration

Configure cookie behavior in your Django settings:

```python
# Cookie security settings
COOKIEJWT_HTTPONLY = True          # HTTP-only cookies (recommended)
COOKIEJWT_SECURE = True           # Set to False in development!
COOKIEJWT_SAMESITE = 'Lax'         # CSRF protection

# Cookie naming and expiration
COOKIEJWT_ACCESS_MAX_AGE = 300     # 5 minutes
COOKIEJWT_REFRESH_MAX_AGE = 86400  # 1 day
COOKIEJWT_PATH = '/'
COOKIEJWT_DOMAIN = None

# Session cookie creation
COOKIEJWT_SET_SESSION_COOKIE = True
```

## Production Configuration

**Important**: The default settings are NOT secure for production use. Configure these settings before deploying:

```python
# Production security settings
COOKIEJWT_SECURE = True            # REQUIRED: HTTPS only
COOKIEJWT_SAMESITE = 'Strict'      # RECOMMENDED: Strong CSRF protection
COOKIEJWT_HTTPONLY = True          # REQUIRED: Prevent XSS attacks

# Optional production optimizations
COOKIEJWT_DOMAIN = 'yourdomain.com'  # Restrict to your domain
```

**Critical**: Never use `COOKIEJWT_SECURE = False` in production. This will send tokens over unencrypted HTTP connections, creating a serious security vulnerability.

## Authentication Behavior

The authentication system works with a fallback mechanism:

1. **Cookie Authentication (Primary)**: The system first looks for JWT tokens in HTTP-only cookies
2. **Header Authentication (Fallback)**: If no valid token is found in cookies, it falls back to standard JWT header authentication (`Authorization: Bearer <token>`)

This means you can use both authentication methods simultaneously:
- Frontend applications can use cookies for seamless authentication
- API clients and mobile apps can use traditional header-based authentication

## Performance Considerations

The `RefreshTokenMiddleware` processes every request (except `/admin/` paths) and performs the following operations:

- Reads and validates access token from cookies
- Makes database queries to authenticate users
- Automatically refreshes expired tokens when possible

This provides seamless user experience but adds processing overhead to each request. Consider this when designing high-traffic applications.

## Usage

### Authentication

Send login credentials to the token endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

The response will set HTTP-only cookies containing JWT tokens.

### Header-based Authentication

Traditional JWT authentication also works:

```bash
curl -X GET http://localhost:8000/api/protected-endpoint/ \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Logout

Blacklist the refresh token:

```bash
curl -X POST http://localhost:8000/api/auth/token/blacklist/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": ""}'
```

This will clear the authentication cookies.

### Frontend Usage

With cookies set, authenticated requests work automatically:

```javascript
// No need to handle tokens manually
fetch('/api/protected-endpoint/', {
  credentials: 'include'  // Include cookies
})
```

## How It Works

1. **Login**: User credentials are exchanged for JWT tokens stored in HTTP-only cookies
2. **Requests**: Cookies are automatically sent with each request
3. **Authentication**: System checks cookies first, then falls back to Authorization header
4. **Refresh**: Middleware automatically refreshes expired access tokens using the refresh token
5. **Logout**: Refresh token is blacklisted and cookies are cleared

## Security Benefits

- **XSS Protection**: HTTP-only cookies prevent JavaScript access to tokens
- **CSRF Mitigation**: SameSite cookie attribute provides CSRF protection
- **Automatic Handling**: No manual token management required on frontend
- **Flexible Integration**: Supports both cookie and header authentication

## API Endpoints

- `POST /api/auth/token/` - Obtain JWT tokens (login)
- `POST /api/auth/token/blacklist/` - Blacklist refresh token (logout)

## Requirements

- Django >= 4.0
- Django REST Framework >= 3.14.0
- djangorestframework-simplejwt >= 5.2.0
- drf-spectacular >= 0.28.0
- Python >= 3.12

## License

MIT License

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/muehlemann-popp/django-cookiejwt).