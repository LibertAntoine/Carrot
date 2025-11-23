import mimetypes
from http import HTTPMethod

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from _config.permissions import IsFileAuthenticated
from _config.services.storage_utils import generate_presigned_url
from actions.models.action_models import generate_thumbnail_path
from actions.serializers.action_thumbnail_serializer import (
    ActionThumbnailSerializer,
)


class ActionThumbnailMixin:
    # TODO: Add better access restrictions.
    @action(
        detail=True,
        methods=[HTTPMethod.GET],
        url_name="thumbnails",
        permission_classes=[IsAuthenticated | IsFileAuthenticated],
        url_path=r"thumbnails/(?P<filename>[\w\-\.]+)",
    )
    def thumbnail(self, request, pk=None, filename=None):
        """Get action thumbnail."""
        thumbnail_action = self.get_object()

        key = generate_thumbnail_path(
            thumbnail_action, filename, uuid_value=filename.split(".")[0]
        )
        if request.file_key and request.file_key != key:
            raise ValidationError("Invalid file key provided.")

        if thumbnail_action.thumbnail.name == key:
            file_obj = thumbnail_action.thumbnail
            content_type = (
                mimetypes.guess_type(thumbnail_action.thumbnail.name)[0]
                or "application/octet-stream"
            )
        else:
            try:
                file_obj = default_storage.open(key, "rb")
            except FileNotFoundError:
                raise Http404("Thumbnail not found")
            content_type = (
                mimetypes.guess_type(key)[0] or "application/octet-stream"
            )
        return FileResponse(file_obj, content_type=content_type)

    @action(
        detail=True,
        methods=[HTTPMethod.PUT],
        name="set_thumbnail",
        url_name="thumbnail",
        url_path="thumbnail",
    )
    def set_thumbnail(self, request, pk=None):
        """Set action thumbnail."""
        # TODO: Manage unreferenced old thumbnails cleanup
        obj = self.get_object()
        serializer = ActionThumbnailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        thumbnail_file = serializer.validated_data["thumbnail"]
        key = generate_thumbnail_path(obj, thumbnail_file.name)
        default_storage.save(key, ContentFile(thumbnail_file.read()))
        return Response(
            {
                "url": generate_presigned_url(key, request),
                "key": key,
            },
            status=status.HTTP_200_OK,
        )
