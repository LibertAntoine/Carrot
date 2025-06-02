from http import HTTPMethod
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actions.serializers.action_thumbnail_serializer import ActionThumbnailSerializer
from django.http import HttpResponse
from django.urls import reverse

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
        if file_name != filename:
            return Response("File not found.", status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(thumbnail_action.thumbnail, content_type="image/png")

    @action(
        detail=True,
        methods=[HTTPMethod.PUT],
        name="set_thumbnail",
        url_name="thumbnail",
        url_path="thumbnail",
    )
    def set_thumbnail(self, request, pk=None):
        """Update action thumbnail."""
        serializer = ActionThumbnailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        thumbnail_action = self.get_object()
        thumbnail_action.thumbnail = serializer.validated_data["thumbnail"]
        thumbnail_action.save()
        file_name = thumbnail_action.thumbnail.name.split("/")[-1]
        return Response(
            {
                "thumbnail_url": request.build_absolute_uri(
                    reverse("actions-thumbnail", args=[thumbnail_action.id, file_name])
                )
            }
        )
