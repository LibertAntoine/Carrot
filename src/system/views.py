from http import HTTPMethod
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from users.permissions import IsAdmin
from jumper.storage_utils import generate_presigned_url
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
        serializer = SystemInfoSerializer(system_info)
        return Response(serializer.data)

    def patch(self, request):
        system_info = SystemInfo.get_instance()
        serializer = SystemInfoSerializer(system_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)


class SystemDefaultBackgroundView(APIView):
    permission_classes = [IsAdmin]

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
                    system_info.default_background_image.name
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
