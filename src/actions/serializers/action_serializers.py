from django.db import transaction
from rest_framework import serializers

from users.serializers.group_serializers import GroupSerializer
from users.serializers.user_serializers import UserSerializer
from .action_data_version_serializers import action_data_serializers

from actions.models.action_models import Action


class ActionSerializer(serializers.ModelSerializer):
    """Serializer for Action model."""
    data = serializers.SerializerMethodField()

    def get_data(self, action: Action) -> dict:
        """Return data type."""
        return {
            'type': action.data.type
        }

    class Meta:
        model = Action
        fields = ["id", "name", "description", "creation_date", "last_update", "data"]
        read_only_fields = ["id", "creation_date", "last_update"]


class ActionPlayableSerializer(ActionSerializer):
    """Serializer for Action model."""
    def get_data(self, action: Action) -> dict:
        """Return action data."""
        serializer = action_data_serializers.get(action.data.type)
        if not serializer:
            return ValueError(f"Data type ${action.data.type} not supported.")
        return serializer(action.data).data

    class Meta:
        model = Action
        fields = ActionSerializer.Meta.fields
        read_only_fields = ActionSerializer.Meta.read_only_fields


class ActionReadDetailedSerializer(ActionPlayableSerializer):
    """Detailed Serializer for Action model."""

    create_by = UserSerializer(read_only=True)
    users = UserSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Action
        fields = ActionSerializer.Meta.fields + [
            "create_by",
            "users",
            "groups",
            "roles",
        ]
        read_only_fields = ActionSerializer.Meta.read_only_fields + [
            "create_by",
        ]


class ActionWriteDetailedSerializer(ActionPlayableSerializer):
    """Detailed Serializer for Action model."""

    class Meta:
        model = Action
        fields = ActionSerializer.Meta.fields + [
            "create_by",
            "users",
            "groups",
            "roles",
        ]
        read_only_fields = ActionSerializer.Meta.read_only_fields + [
            "create_by",
        ]

    def create(self, validated_data):
        """Create Action."""
        with transaction.atomic():
            data = self.initial_data.get("data")
            if not data:
                raise serializers.ValidationError({"data": "This field is required."})
            if not data.get("type"):
                raise serializers.ValidationError(
                    {"data.type": "This field is required."}
                )
            data_serializer = action_data_serializers.get(data["type"])
            if not data_serializer:
                raise serializers.ValidationError(
                    f"Data type ${data['type']} not supported."
                )
            data_serializer = data_serializer(data=data)
            data_serializer.is_valid(raise_exception=True)
            action_data = data_serializer.save()
            validated_data["data"] = action_data
            return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update Action."""
        with transaction.atomic():
            data = self.initial_data.pop("data", None)
            if data:
                data_serializer = action_data_serializers.get(instance.data.type)
                if not data_serializer:
                    raise ValueError(f"Data type ${instance.data.type} not supported.")
                data_instance = instance.data
                data_serializer = data_serializer(data_instance, data)
                data_serializer.is_valid(raise_exception=True)
                data_serializer.save()
            return super().update(instance, validated_data)
