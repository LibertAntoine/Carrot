from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Config Views
@api_view(["GET"])
def get_app_info(request):
    providers = []

    if settings.PASSWORD_BASED_AUTHENTICATION:
        providers.append(
            {
                "id": "email",
                "name": "Email",
                "authUrl": "/auth",
                "logoutUrl": "/auth/logout",
            }
        )

    if settings.OIDC_ENABLED:
        providers.append(
            {
                "id": "oidc",
                "name": settings.OIDC_PROVIDER_NAME,
                "authUrl": "/oidc/auth",
                "logoutUrl": "/oidc/logout",
            }
        )

    return Response(
        {
            "name": "Carrot",
            "version": settings.APP_VERSION,
            "commit": settings.APP_COMMIT,
            "build_date": settings.APP_BUILD_DATE,
            "scim_enabled": settings.SCIM_ENABLED,
            "reset_password_enabled": settings.PASSWORD_BASED_AUTHENTICATION
            and settings.EMAIL_HOST,
            "providers": providers,
        }
    )
