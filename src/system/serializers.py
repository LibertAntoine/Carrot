from rest_framework import serializers
from .models import SystemInfo
from django.core.exceptions import ValidationError
from jumper.storage_utils import generate_presigned_url


class SystemInfoSerializer(serializers.ModelSerializer):
    default_background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = SystemInfo
        fields = [
            "allow_action_workspaces",
            "default_background_image_url",
            "allow_background_image",
            "allow_user_custom_background_image",
        ]
        read_only_fields = ["default_background_image_url"]

    def get_default_background_image_url(self, obj: SystemInfo) -> str:
        """Return system default background image url."""
        if bool(obj.default_background_image):
            return generate_presigned_url(obj.default_background_image.name)
        return None


class SystemInfoDefaultBackgroundImageSerializer(serializers.ModelSerializer):
    """Serializer for SystemInfo default background image."""
    PICTURE_MAX_SIZE_MB = 100

    class Meta:
        model = SystemInfo
        fields = [
            "id",
            "default_background_image",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_default_background_image(self, value):
        """Validate default background image."""
        if not value:
            return value
        if value.size > self.PICTURE_MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image size must be less than {self.PICTURE_MAX_SIZE_MB}Mo."
            )
        return value
