from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from mozilla_django_oidc.views import (
    OIDCAuthenticationRequestView,
    OIDCAuthenticationCallbackView,
)
from urllib.parse import urlparse, parse_qs
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.conf import settings
from users.models import User
from .jwt import set_jwt_tokens, get_tokens_for_user

class OIDCAuthCallback(OIDCAuthenticationCallbackView):
    def login_success(self):
        tokens = get_tokens_for_user(self.user)
        state = self.request.GET.get('state')
        custom_params = self.request.session.pop(f'oidc_custom_params_{state}', {})
        if custom_params.get("client") == "jumper":
            response = HttpResponse(status=302)
            redirect_url = (
                f"jumper://oidc-auth-callback?"
                f"status=success&provider={self.request.get_host()}&"
                f"access_token={tokens['access']}&refresh_token={tokens['refresh']}"
            )
            response['Location'] = redirect_url
            return response
        else:
            response = HttpResponse(status=204)
            set_jwt_tokens(tokens, response, self.request, with_refresh=False)
            response.delete_cookie("sessionid", path="/")
            return response

class OIDCAuthRequest(OIDCAuthenticationRequestView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        redirect_url = response.get('Location')
        if not redirect_url:
            return response  # fail-safe
        parsed = urlparse(redirect_url)
        query_params = parse_qs(parsed.query)
        state = query_params.get('state', [None])[0]

        if state and request.GET:
            request.session[f'oidc_custom_params_{state}'] = request.GET.dict()
            request.session.modified = True
        return response

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        """Return all users matching the specified sub or email."""
        user = None
        sub = claims.get("sub")
        if sub:
            user = self.UserModel.objects.filter(scim_external_id=sub)
            if not user.exists():
                user = None
        email = claims.get("email")
        if not user and email:
            user = self.UserModel.objects.filter(email__iexact=email)
        if not user:
            user = self.UserModel.objects.none()
        return user

    def create_user(self, claims):
        """Overrides Authentication Backend so that Django users are
        created with the keycloak preferred_username.
        If nothing found matching the email, then try the username.
        """
        user = User.objects.filter(email=claims.get("email")).first()
        if not user:
            name = claims.get("given_name", "")
            split_name = name.split(" ")
            first_name = split_name[0] if " " in name else name
            last_name = " ".join(split_name[1:]) if " " in name else ""
            user = User.objects.create(
                email=claims.get("email"),
                username=claims.get(settings.OIDC_USERNAME_ATTRIBUTE),
                first_name=first_name,
                last_name=last_name,
                scim_external_id=claims.get("sub"),
            )
        user.username = claims.get(settings.OIDC_USERNAME_ATTRIBUTE)
        user.save()
        return user

    def update_user(self, user, claims):
        user.email = claims.get("email")
        user.username = claims.get(settings.OIDC_USERNAME_ATTRIBUTE)
        user.save()
        return user
