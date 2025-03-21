from rest_framework import serializers

from .group_serializers import GroupSerializer
from .user_serializers import UserSerializer
from users.models import Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "description",
            "users",
            "groups",
            "actions",
            "creation_date",
            "last_update",
            "create_by",
        ]
        read_only_fields = ["id", "creation_date", "last_update", "create_by"]


class RoleDetailedSerializer(RoleSerializer):
    """Detailed Serializer for Role model."""
    groups = GroupSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)


