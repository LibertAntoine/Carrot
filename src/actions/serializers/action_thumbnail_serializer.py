from django.core.exceptions import ValidationError
from rest_framework import serializers


class ActionThumbnailSerializer(serializers.Serializer):
    """Serializer for Action thumbnail."""
    PICTURE_MAX_SIZE_MB = 100
    thumbnail = serializers.ImageField(required=True) 

    def validate_thumbnail(self, value):
        """Validate thumbnail."""
        valid_formats = ("PNG", "JPEG", "GIF")
        if value.image.format not in valid_formats:
            raise ValidationError({"error": "Invalid thumbnail file type."})

        if value.size > self.PICTURE_MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image size must be less than {self.PICTURE_MAX_SIZE_MB}Mo."
            )
        return value
