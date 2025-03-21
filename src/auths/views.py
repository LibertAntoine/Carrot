from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt import views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .jwt import set_jwt_tokens, get_tokens_for_user, get_cookie_params

# JWT Views
@api_view(['POST'])
def login_view(request):
    data = request.data
    response = Response()
    email = data.get('email', None)
    password = data.get('password', None)
    user = authenticate(email=email, password=password)

    if user is not None:
        if user.is_active:
            tokens = get_tokens_for_user(user)
            set_jwt_tokens(tokens, response, request)
            return response
        else:
            return Response({"No active": "This account is not active"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"Invalid": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except jwt_exceptions.TokenError:
        pass
    cookie_params = get_cookie_params()
    response = Response(status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], **cookie_params)
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'], **cookie_params)
    response.delete_cookie("csrftoken", **cookie_params)
    return response


class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    def validate(self, attrs):
        refresh_token = self.context['request'].COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        if refresh_token:
            attrs['refresh'] = self.context['request'].COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        if attrs.get('refresh'):
            return super().validate(attrs)
        else:
            raise jwt_exceptions.InvalidToken(
                f'No valid refresh token found.')


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('access'):
            set_jwt_tokens(response.data, response, request, with_refresh=False)
        return super().finalize_response(request, response, *args, **kwargs)


# Config Views
@api_view(['GET'])
def get_config(request):
    providers = []

    if settings.JWT_ENABLED:
        providers.append({
            'id': 'email',
            'name': 'Email',
            'authUrl': '/auth',
            'logoutUrl': '/auth/logout',
        })

    if settings.OIDC_ENABLED:
        providers.append({
            'id': 'oidc',
            'name': settings.OIDC_PROVIDER_NAME,
            'authUrl': '/oidc/auth',
            'logoutUrl': '/oidc/logout',
        })

    return Response({
        'scim_enabled': settings.SCIM_ENABLED,
        'providers': providers
    })


@api_view(["GET"])
def get_auth_status(request):
    return Response({"authenticated": request.user.is_authenticated})
