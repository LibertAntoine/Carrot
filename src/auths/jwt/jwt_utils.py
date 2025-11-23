from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
)
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

BROWSER_USER_AGENTS = [
    "Brave",
    "Chrome",
    "Chrome Mobile",
    "Chrome Mobile iOS",
    "Edge",
    "Firefox",
    "Mobile Safari",
    "Opera",
    "Safari",
    "Vivaldi",
]


class JwtCookiesAuthentication(JWTAuthentication):
    def authenticate(self, request):
        simple_jwt_settings = getattr(settings, "SIMPLE_JWT", {})
        if (
            request.user_agent.browser.family not in BROWSER_USER_AGENTS
            or not simple_jwt_settings.get("AUTH_COOKIE_ENABLED", False)
        ):
            return super().authenticate(request)

        raw_token = request.COOKIES.get(simple_jwt_settings["AUTH_COOKIE_NAME"])
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            return None


def set_jwt_tokens(tokens, response, request, with_refresh=True):
    simple_jwt_settings = getattr(settings, "SIMPLE_JWT", {})
    if (
        simple_jwt_settings.get("AUTH_COOKIE_ENABLED", False)
        and request.user_agent.browser.family in BROWSER_USER_AGENTS
    ):
        cookies_config_base = {
            "secure": simple_jwt_settings.get("AUTH_COOKIE_SECURE", True),
            "httponly": simple_jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
            "samesite": simple_jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
            "domain": simple_jwt_settings.get("AUTH_COOKIE_DOMAIN", None),
            "path": simple_jwt_settings.get("AUTH_COOKIE_PATH", "/"),
        }

        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_NAME"],
            value=tokens["access"],
            expires=timezone.now()
            + simple_jwt_settings.get(
                "ACCESS_TOKEN_LIFETIME", timedelta(days=1)
            ),
            **cookies_config_base,
        )

        if with_refresh:
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_NAME"],
                value=tokens["refresh"],
                expires=timezone.now()
                + simple_jwt_settings.get(
                    "REFRESH_TOKEN_LIFETIME", timedelta(days=30)
                ),
                **cookies_config_base,
            )
        response.data = {"Success": "Login successfully"}
        if response.data.get("access"):
            del response.data["access"]
        return
    response.data = tokens if with_refresh else {"access": tokens["access"]}


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def backlist_user_tokens(user):
    """Blacklist all tokens for a user."""
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def backlist_tokens(tokens: list[str]):
    """Blacklist all tokens in the provided list."""
    for token in OutstandingToken.objects.filter(token__in=tokens):
        BlacklistedToken.objects.get_or_create(token=token)
