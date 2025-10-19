from rest_framework import serializers
from users.serializers.user_serializers import ShortUserSerializer
from users.serializers.role_serializers import RoleDetailedSerializer
from users.serializers.group_serializers import GroupDetailedSerializer
from .models import Workspace
from users.models import User, Group, Role


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "name", "description", "created_at", "updated_at", "is_active"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class DetailedWorkspaceSerializer(WorkspaceSerializer):
    created_by = ShortUserSerializer(read_only=True)
    users = ShortUserSerializer(many=True, read_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, source="users"
    )
    groups = GroupDetailedSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, write_only=True, source="groups"
    )
    roles = RoleDetailedSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, write_only=True, source="roles"
    )

    class Meta(WorkspaceSerializer.Meta):
        fields = WorkspaceSerializer.Meta.fields + [
            "created_by",
            "users",
            "groups",
            "roles",
            "user_ids",
            "group_ids",
            "role_ids",
        ]
