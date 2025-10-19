from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """Custom permission to only allow admins to view or edit it."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and request.user.is_admin


class IsUserManager(BasePermission):
    """Custom permission to only allow user managers to view or edit it."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and request.user.is_user_manager


class IsActionManager(BasePermission):
    """Custom permission to only allow action managers to view or edit it."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and request.user.is_action_manager
