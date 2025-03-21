from typing import Any
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import permissions

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