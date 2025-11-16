from users.models import UserPreferences
from rest_framework import serializers
from jumper.services.storage_utils import generate_presigned_url
from rest_framework.exceptions import ValidationError


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for User Preferences."""

    custom_background_image_url = serializers.SerializerMethodField()

    def get_custom_background_image_url(self, obj: UserPreferences) -> str:
        """Return user's custom background image url."""
        if bool(obj.custom_background_image):
            return generate_presigned_url(obj.custom_background_image.name, self.context['request'])
        return None

    class Meta:
        model = UserPreferences
        fields = [
            "id",
            "disable_default_background_image",
            "custom_background_image_url",
        ]
        read_only_fields = [
            "id",
            "user",
        ]


class UserPreferenceCustomBackgroundImageSerializer(serializers.ModelSerializer):
    """Serializer for User Preferences background image."""
    PICTURE_MAX_SIZE_MB = 10

    class Meta:
        model = UserPreferences
        fields = [
            "id",
            "custom_background_image",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_custom_background_image(self, value):
        """Validate custom background image."""
        if not value:
            return value
        if value.size > self.PICTURE_MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image size must be less than {self.PICTURE_MAX_SIZE_MB}Mo."
            )
        return value
