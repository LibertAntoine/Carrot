from .models import Workspace
from django.db.models import Q
from rest_framework.permissions import BasePermission

class IsWorkspaceMember(BasePermission):
    """Custom permission to only allow members of a workspace to view or edit it."""

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return Workspace.objects.filter(
            Q(pk=obj.pk),
            Q(users=user)
            | Q(groups__user_set=user)
            | Q(roles__users=user)
            | Q(roles__groups__user_set=user),
        ).exists()
