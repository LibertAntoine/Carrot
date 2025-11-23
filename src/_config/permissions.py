from typing import Any
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import permissions
from django.core import signing
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class IsOwner(BasePermission):
    """Custom permission to only allow owners of an object to view or edit it."""
    def has_object_permission(self, request: Request, view: APIView, obj: Any):
        return obj == request.user

    def has_permission(self, request: Request, view: APIView):
        return request.method != "POST"

class IsReadOnly(BasePermission):
    """Custom permission to only allow read-only requests."""
    def has_permission(self, request: Request, view: APIView):
        return request.method in permissions.SAFE_METHODS
    

class IsFileAuthenticated(BasePermission):
    """Custom permission to check if the user is authenticated for file access via query token."""
    def has_permission(self, request: Request, view: APIView):
        token = request.GET.get("token")
        if not token:
            raise AuthenticationFailed("Missing token")

        try:
            data = signing.loads(token, salt="local-file-token")
        except signing.BadSignature:
            raise AuthenticationFailed("Invalid token")

        if timezone.now().timestamp() > data["exp"]:
            raise AuthenticationFailed("Token expired")

        user_id = data.get("user")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        request.user = user
        request.file_key = data["file"]

        return True
