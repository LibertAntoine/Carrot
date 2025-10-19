from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from .models import SystemInfo
from .serializers import SystemInfoSerializer


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