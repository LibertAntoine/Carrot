from http import HTTPMethod
import mimetypes
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from rest_framework.decorators import api_view, permission_classes
from jumper.permissions import IsFileAuthenticated
from jumper.services.storage_utils import generate_presigned_url
from .models import SystemInfo
from .serializers import (
    SystemInfoSerializer,
    SystemInfoDefaultBackgroundImageSerializer,
)

class SystemInfoView(APIView):
    """Get or update system info."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        elif self.request.method == "PATCH":
            return [IsAdmin()]
        return super().get_permissions()

    def get(self, request):
        system_info = SystemInfo.get_instance()
        serializer = SystemInfoSerializer(system_info, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        system_info = SystemInfo.get_instance()
        serializer = SystemInfoSerializer(
            system_info, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated | IsFileAuthenticated])
def system_default_background_file(request, pk=None, filename=None):
    """Get system default background."""
    system_info = SystemInfo.get_instance()
    if (
        request.file_key
        and request.file_key != system_info.default_background_image.name
    ):
        raise ValidationError("Invalid file key provided.")
    content_type = mimetypes.guess_type(
        system_info.default_background_image.name
    )[0] or "application/octet-stream"
    return FileResponse(
        system_info.default_background_image, content_type=content_type
    )

class SystemDefaultBackgroundView(APIView):
    permission_classes = [IsAuthenticated | IsFileAuthenticated, IsAdmin]

    def put(self, request):
        system_info = SystemInfo.get_instance()
        serializer = SystemInfoDefaultBackgroundImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        system_info.default_background_image = serializer.validated_data[
            "default_background_image"
        ]
        system_info.save()
        return Response(
            {
                "default_background_image_url": generate_presigned_url(
                    system_info.default_background_image.name,
                    request,
                )
            }
        )

    def delete(self, request):
        system_info = SystemInfo.get_instance()
        system_info.default_background_image.delete()
        system_info.save()
        return Response(
            "Default background image deleted.", status=status.HTTP_204_NO_CONTENT
        )
