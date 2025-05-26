from django.core.exceptions import ValidationError
from rest_framework import serializers
from actions.models import Action


class ActionThumbnailSerializer(serializers.ModelSerializer):
    """Serializer for Action thumbnail."""

    PICTURE_MAX_SIZE_MB = 100

    class Meta:
        model = Action
        fields = [
            "id",
            "thumbnail",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_thumbnail(self, value):
        """Validate thumbnail."""
        if not value:
            return value
        if value.size > self.PICTURE_MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"Image size must be less than {self.PICTURE_MAX_SIZE_MB}Mo."
            )
        return value