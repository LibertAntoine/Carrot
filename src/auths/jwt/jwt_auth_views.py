import logging

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt import exceptions as jwt_exceptions
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework_simplejwt import views as jwt_views

from .jwt_utils import (
    BROWSER_USER_AGENTS,
    backlist_tokens,
    get_tokens_for_user,
    set_jwt_tokens,
)

logger = logging.getLogger("django")


@api_view(["POST"])
def login(request):
    data = request.data
    response = Response()
    email = data.get("email", None)
    password = data.get("password", None)
    user = authenticate(email=email, password=password)

    if user is not None:
        if user.is_active:
            tokens = get_tokens_for_user(user)
            set_jwt_tokens(tokens, response, request)
            return response
        else:
            return Response(
                {"No active": "This account is not active"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"Invalid": "Invalid email or password"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def set_tokens(request):
    data = request.data
    response = Response()
    access_token = data.get("access", None)
    refresh_token = data.get("refresh", None)
    if access_token and refresh_token:
        try:
            set_jwt_tokens(
                {"access": access_token, "refresh": refresh_token},
                response,
                request,
                with_refresh=True,
            )
            return response
        except jwt_exceptions.TokenError:
            return Response(
                {"Invalid": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    if (
        settings.SIMPLE_JWT.get("AUTH_COOKIE_ENABLED", False)
        and request.user_agent.browser.family in BROWSER_USER_AGENTS
    ):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_NAME"]
        )
    else:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh", None)
    if not refresh_token:
        return Response(
            {"refresh": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    backlist_tokens([refresh_token])
    response = Response(status=status.HTTP_204_NO_CONTENT)
    if settings.SIMPLE_JWT.get("AUTH_COOKIE_ENABLED", False):
        cookie_params = {
            "path": settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            "domain": settings.SIMPLE_JWT["AUTH_COOKIE_DOMAIN"],
        }
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_NAME"], **cookie_params
        )
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_NAME"], **cookie_params
        )
    return response


class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    refresh = serializers.CharField(required=False)

    def validate(self, attrs):
        if settings.SIMPLE_JWT.get("AUTH_COOKIE_ENABLED", False):
            refresh_token = self.context["request"].COOKIES.get(
                settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_NAME"]
            )
            if refresh_token:
                attrs["refresh"] = self.context["request"].COOKIES.get(
                    settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH_NAME"]
                )
            logger.warning(refresh_token)
        if attrs.get("refresh"):
            return super().validate(attrs)
        else:
            raise serializers.ValidationError(
                {"refresh": "This field is required."}
            )


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("access"):
            set_jwt_tokens(response.data, response, request, with_refresh=False)
        response = super().finalize_response(request, response, *args, **kwargs)
        if (
            request.user_agent.browser.family in BROWSER_USER_AGENTS
            and settings.SIMPLE_JWT.get("AUTH_COOKIE_ENABLED", False)
        ):
            response.data.pop("access", None)
        return response


@api_view(["GET"])
def get_auth_status(request):
    return Response({"authenticated": request.user.is_authenticated})
