import mimetypes
from http import HTTPMethod
from urllib import response

from django.forms import ValidationError
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from _config.permissions import IsFileAuthenticated, IsOwner
from _config.services.storage_utils.presigned_url import generate_presigned_url
from users.models import UserPreferences
from users.permissions import IsAdmin
from users.serializers.user_preferences_serializers import (
    UserPreferenceCustomBackgroundImageSerializer,
    UserPreferencesSerializer,
)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """API endpoint that allows user preferences to be viewed or edited."""

    queryset = UserPreferences.objects.all()
    model = UserPreferences
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_admin:
            return queryset
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        return response.Response(
            {"detail": "Method 'POST' not allowed."},
            status=response.status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return response.Response(
            {"detail": "Method 'DELETE' not allowed."},
            status=response.status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        detail=True,
        methods=[HTTPMethod.PUT, HTTPMethod.DELETE],
        url_name="background-image",
        url_path="background-image",
    )
    def set_background_image(self, request, pk=None):
        """Update user background image."""
        userPreferences = self.get_object()
        if request.method == HTTPMethod.DELETE:
            userPreferences.custom_background_image.delete()
            userPreferences.save()
            return Response(
                "Background image deleted.", status=status.HTTP_204_NO_CONTENT
            )
        else:
            serializer = UserPreferenceCustomBackgroundImageSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            userPreferences.custom_background_image = serializer.validated_data[
                "custom_background_image"
            ]
            userPreferences.save()
            return Response(
                {
                    "custom_background_image_url": generate_presigned_url(
                        userPreferences.custom_background_image.name,
                        request,
                    )
                }
            )

    @action(
        detail=True,
        methods=[HTTPMethod.GET],
        url_name="backgrounds",
        permission_classes=[IsAuthenticated | IsFileAuthenticated],
        url_path=r"backgrounds/(?P<filename>[\w\-\.]+)",
    )
    def user_preference_background_file(self, request, pk=None, filename=None):
        """Get user preference background."""
        user_preferences = self.get_object()
        if (
            request.file_key
            and request.file_key
            != user_preferences.custom_background_image.name
        ):
            raise ValidationError("Invalid file key provided.")
        content_type = (
            mimetypes.guess_type(user_preferences.custom_background_image.name)[
                0
            ]
            or "application/octet-stream"
        )
        return FileResponse(
            user_preferences.custom_background_image, content_type=content_type
        )
