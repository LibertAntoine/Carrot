import mimetypes
from http import HTTPMethod
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.urls import reverse
from actions.models.action_models import THUMBNAILS_URL_BASE
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actions.serializers.action_thumbnail_serializer import ActionThumbnailSerializer


class ActionThumbnailMixin:
    @action(
        detail=True,
        methods=[HTTPMethod.GET],
        url_name="thumbnail",
        permission_classes=[IsAuthenticated],
        url_path=r"thumbnail/(?P<filename>[\w\-\.]+)",
    )
    def thumbnail(self, request, pk=None, filename=None):
        """Get action thumbnail."""
        thumbnail_action = self.get_object()
        file_name_without_ext, ext = (filename.rsplit(".", 1) + [""])[:2]

        # Handle temporary thumbnails
        if file_name_without_ext == "tmp":
            tmp_path = thumbnail_action.get_tmp_thumbnail_url(ext)
            content_type, _ = mimetypes.guess_type(tmp_path)
            try:
                return FileResponse(
                    default_storage.open(tmp_path, "rb"),
                    content_type=content_type or "image/png",
                )
            except FileNotFoundError:
                return Response(
                    "Temporary thumbnail not found.",
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Handle permanent thumbnails
        file_path = f"{THUMBNAILS_URL_BASE}/{thumbnail_action.id}/{filename}"
        try:
            # If the model field matches the requested path → serve directly (fast path)
            if thumbnail_action.thumbnail.name == file_path:
                file_obj = thumbnail_action.thumbnail
                content_type = mimetypes.guess_type(file_obj.name)[0] or "image/png"
            else:
                # Otherwise read from storage
                file_obj = default_storage.open(file_path, "rb")
                content_type = mimetypes.guess_type(filename)[0] or "image/png"
            return FileResponse(file_obj, content_type=content_type)
        except FileNotFoundError:
            return Response(
                "Thumbnail not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        detail=True,
        methods=[HTTPMethod.PUT],
        name="set_thumbnail",
        url_name="thumbnail",
        url_path="thumbnail",
    )
    def set_thumbnail(self, request, pk=None):
        """Set action thumbnail."""
        obj = self.get_object()
        serializer = ActionThumbnailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thumbnail_file = serializer.validated_data["thumbnail"]
        ext = mimetypes.guess_extension(thumbnail_file.content_type)
        tmp_path = obj.get_tmp_thumbnail_url(ext.lstrip("."))
        default_storage.save(tmp_path, ContentFile(thumbnail_file.read()))
        return Response(
            {
                "thumbnail_url": request.build_absolute_uri(
                    reverse("actions-thumbnail", args=[obj.id, f"tmp{ext}"])
                )
            },
            status=status.HTTP_200_OK,
        )
