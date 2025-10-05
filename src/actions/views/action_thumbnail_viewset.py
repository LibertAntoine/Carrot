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
        if not thumbnail_action.thumbnail:
            return Response("No thumbnail.", status=status.HTTP_404_NOT_FOUND)

        file_name = thumbnail_action.thumbnail.name.split("/")[-1]
        file_name_without_ext = filename.rsplit(".", 1)[0]
        ext = filename.rsplit(".", 1)[-1]

        if file_name_without_ext == "tmp":
            tmp_path = thumbnail_action.get_tmp_thumbnail_url(ext)
            if not default_storage.exists(tmp_path):
                return Response(
                    "Temporary thumbnail not found.", status=status.HTTP_404_NOT_FOUND
                )
            content_type, _ = mimetypes.guess_type(tmp_path)
            return FileResponse(
                default_storage.open(tmp_path, "rb"),
                content_type=content_type or "image/png",
            )
        file_path = f"{THUMBNAILS_URL_BASE}/{thumbnail_action.id}/{filename}"
        if not default_storage.exists(file_path):
            return Response("Thumbnail not found.", status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            default_storage.open(file_path, "rb"),
            content_type="image/png",
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
