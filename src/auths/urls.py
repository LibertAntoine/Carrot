from django.urls import path, include
from django.conf import settings
from .reset_password.reset_password_views import (
    request_reset_password,
    confirm_reset_password,
    verify_reset_password_otp,
)
from .oidc.oidc_auth_views import OIDCAuthRequest, OIDCAuthCallback
from .jwt.jwt_auth_views import (
    login,
    set_tokens,
    CookieTokenRefreshView,
    logout,
    get_auth_status,
)


urlpatterns = [
    # Authentication configuration getter route
    path("auth/status", get_auth_status, name="auth-status"),
    path("auth/logout", logout, name="token_verify"),
    path("auth/refresh", CookieTokenRefreshView.as_view(), name="token_refresh"),
]

if getattr(settings, "PASSWORD_BASED_AUTHENTICATION", True):
    urlpatterns += [
        path("auth", login, name="token_obtain_pair"),
        path(
            "auth/password-reset/request",
            request_reset_password,
            name="reset-password-request",
        ),
        path(
            "auth/password-reset/verify",
            verify_reset_password_otp,
            name="reset-password-verify",
        ),
        path(
            "auth/password-reset/confirm",
            confirm_reset_password,
            name="reset-password-confirm",
        ),
    ]

if getattr(settings, "OIDC_ENABLED", False):
    urlpatterns += [
        path("auth/set-tokens", set_tokens, name="token_obtain_pair"),
        path("oidc/auth/", OIDCAuthRequest.as_view(), name="oidc_auth_request"),
        path("oidc/callback/", OIDCAuthCallback.as_view(), name="oidc_auth_callback"),
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]
