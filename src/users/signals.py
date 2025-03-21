from users.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings


def create_default_user(sender, **kwargs) -> None:
    """Create default user after migrations."""
    if User.objects.count() == 0:
        User.objects.create(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=make_password(settings.ADMIN_PASSWORD),
            is_superuser=True,
        )