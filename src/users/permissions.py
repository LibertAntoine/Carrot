from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """Custom permission to only allow admins to view or edit it."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and (
            request.user.is_superuser or request.user.is_superuser_group_member
        )
