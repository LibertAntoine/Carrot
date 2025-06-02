from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.conf import settings

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
        if request.user_agent.browser.family not in BROWSER_USER_AGENTS:
            return super().authenticate(request)

        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            return None


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_jwt_tokens(tokens, response, request, with_refresh=True):
    if request.user_agent.browser.family in BROWSER_USER_AGENTS:
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=tokens["access"],
            expires=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
            path="/",
        )

        if with_refresh:
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                value=tokens["refresh"],
                expires=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                domain=settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
                path="/",
            )
    if (
        request.user_agent.browser.family not in BROWSER_USER_AGENTS
        or request.headers.get("X-Client-Agent") == "jumper-client"
    ):
        response.data = tokens if with_refresh else {"access": tokens["access"]}
    else:
        response.data = {"Success": "Login successfully"}
        if response.data.get("access"):
            del response.data["access"]


def get_cookie_params():
    return {
        "path": "/",
        "domain": settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
    }
