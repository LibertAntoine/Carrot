from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from users.models import User


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC authentication backend.
    """

    def filter_users_by_claims(self, claims):
        """
        Return a queryset of users matching the given OIDC claims.
        """
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
        """
        Creates a new Django user based on OIDC claims.
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
        """
        Updates an existing Django user with new OIDC claim values.
        """
        user.scim_external_id = claims.get("sub")
        user.email = claims.get("email")
        user.username = claims.get(settings.OIDC_USERNAME_ATTRIBUTE)
        user.save()
        return user
