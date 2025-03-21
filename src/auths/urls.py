from django.urls import path, include
from django_rest_passwordreset.views import (
    reset_password_confirm,
    reset_password_request_token,
    reset_password_validate_token,
)
from django.conf import settings
from .oidc import OIDCAuthRequest, OIDCAuthCallback
from .views import (
    get_config,
    login_view,
    CookieTokenRefreshView,
    logout_view,
    get_auth_status,
)


urlpatterns = [
    # Authentication configuration getter route
    path("auth/status", get_auth_status, name="auth-status"),
    path("auth/config", get_config, name="auth-config"),
    path("auth/logout", logout_view, name="token_verify"),
    path("auth/refresh", CookieTokenRefreshView.as_view(), name="token_refresh"),
]

if settings.JWT_ENABLED:
    urlpatterns += [
        path("auth", login_view, name="token_obtain_pair"),
        path(
            "password-reset/validate_token",
            reset_password_validate_token,
            name="reset-password-validate",
        ),
        path(
            "password-reset/confirm",
            reset_password_confirm,
            name="reset-password-confirm",
        ),
        path(
            "password-reset",
            reset_password_request_token,
            name="reset-password-request",
        ),
    ]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path("oidc/auth/", OIDCAuthRequest.as_view(), name="oidc_auth_request"),
        path("oidc/callback/", OIDCAuthCallback.as_view(), name="oidc_auth_callback"),
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]
