from django.urls import reverse
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from django.conf import settings

from users.models import User


class ShortUserSerializer(serializers.ModelSerializer):
    """Serializer for User model with limited fields."""
    profile_picture_url = serializers.SerializerMethodField()

    def get_profile_picture_url(self, user: User) -> str:
        """Return profile picture url."""
        if bool(user.profile_picture):
            request = self.context.get("request")
            file_name = user.profile_picture.name.split("/")[-1]
            return request.build_absolute_uri(
                reverse("user-profile", args=[user.id, file_name])
            )
        return None

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_picture_url"
        ]
        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_picture_url"
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    profile_picture_url = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    external_id = serializers.SerializerMethodField()
    get_external_id = lambda self, obj: obj.scim_external_id

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "creation_date",
            "last_update",
            "is_active",
            "password",
            "profile_picture_url",
            "system_role",
            "external_id",
            "groups",
            "is_superuser_group_member",
        ]
        read_only_fields = [
            "id",
            "creation_date",
            "last_update",
            "profile_picture_url",
            "external_id",
            "groups",
            "is_superuser_group_member",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def get_profile_picture_url(self, user: User) -> str:
        """Return profile picture url."""
        if bool(user.profile_picture):
            request = self.context.get("request")
            file_name = user.profile_picture.name.split("/")[-1]
            return request.build_absolute_uri(
                reverse("user-profile", args=[user.id, file_name])
            )
        return None

    def get_groups(self, user: User) -> list:
        """Return user groups."""
        if not settings.SCIM_ENABLED:
            return []
        return user.groups.all().values_list("id", flat=True)

    def validate_password(self, value: str) -> str:
        """Validate password."""
        if len(value) < 5:
            raise ValidationError("Password must be at least 5 characters.")
        return value

    def create(self, validated_data: dict) -> User:
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)
        return user

    def update(self, user: User, validated_data: dict) -> User:
        if self.instance.scim_external_id and (
            settings.OIDC_ENABLED or settings.SCIM_ENABLED
        ):
            if (
                validated_data.get("username")
                and validated_data["username"] != user.username
            ):
                raise serializers.ValidationError(
                    {
                        "username": "You can't change the username for a user managed by SSO"
                    }
                )
            if validated_data.get("email") and validated_data["email"] != user.email:
                raise serializers.ValidationError(
                    {"email": "You can't change email for a user managed by SSO."}
                )
            if validated_data.get("password"):
                raise serializers.ValidationError(
                    {"password": "You can't change password for a user managed by SSO."}
                )
            if (
                validated_data.get("is_active")
                and validated_data["is_active"] != user.is_active
            ):
                raise serializers.ValidationError(
                    {
                        "is_active": "You can't change is_active for a user managed by SSO."
                    }
                )
        password = validated_data.pop("password", None)
        if password is not None:
            validated_data["password"] = make_password(password)
        return super().update(user, validated_data)


class UserProfilePictureSerializer(serializers.ModelSerializer):
    """Serializer for User profile picture."""

    PICTURE_MAX_SIZE_MB = 10

    class Meta:
        model = User
        fields = [
            "id",
            "profile_picture",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_profile_picture(self, value):
        """Validate profile picture."""
        if not value:
            return value
        if value.size > self.PICTURE_MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image size must be less than {self.PICTURE_MAX_SIZE_MB}Mo."
            )
        return value
