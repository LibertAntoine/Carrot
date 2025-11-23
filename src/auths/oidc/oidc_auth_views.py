from urllib.parse import parse_qs, urlparse

from django.http import HttpResponse
from mozilla_django_oidc.views import (
    OIDCAuthenticationCallbackView,
    OIDCAuthenticationRequestView,
)
from rest_framework.permissions import AllowAny

from auths.jwt.jwt_utils import get_tokens_for_user, set_jwt_tokens


class OIDCAuthCallback(OIDCAuthenticationCallbackView):
    """
    Custom OIDC callback view that handles successful authentication.
    """

    def login_success(self):
        """
        Called on successful OIDC authentication.
        """
        tokens = get_tokens_for_user(self.user)
        state = self.request.GET.get("state")
        custom_params = self.request.session.pop(
            f"oidc_custom_params_{state}", {}
        )
        if custom_params.get("client") == "jumper":
            response = HttpResponse(status=302)
            redirect_url = (
                f"jumper://oidc-auth-callback?"
                f"status=success&provider={self.request.get_host()}&"
                f"access_token={tokens['access']}&"
                f"refresh_token={tokens['refresh']}"
            )
            response["Location"] = redirect_url
            return response
        else:
            response = HttpResponse(status=204)
            set_jwt_tokens(tokens, response, self.request, with_refresh=False)
            response.delete_cookie("sessionid", path="/")
            return response


class OIDCAuthRequest(OIDCAuthenticationRequestView):
    """
    Custom OIDC authentication request view.

    This view initiates the OIDC authentication flow and stores any
    client-specific parameters in the session for retrieval after the callback.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to initiate the OIDC authentication.
        """
        response = super().get(request, *args, **kwargs)

        redirect_url = response.get("Location")
        if not redirect_url:
            return response  # fail-safe
        parsed = urlparse(redirect_url)
        query_params = parse_qs(parsed.query)
        state = query_params.get("state", [None])[0]

        if state and request.GET:
            request.session[f"oidc_custom_params_{state}"] = request.GET.dict()
            request.session.modified = True
        return response
