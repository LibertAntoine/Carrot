from rest_framework import serializers
from actions.models.action_data_models import (
    PythonActionData,
    LinkActionData,
    WindowsCMDActionData,
    ActionData,
)


class ActionDataSerializer(serializers.ModelSerializer):
    """Serializer for ActionData model."""

    class Meta:
        abstract = True
        model = ActionData
        fields = ["id", "type"]
        read_only_fields = ["id", "type"]


class PythonActionDataSerializer(ActionDataSerializer):
    """Serializer for PythonActionData model."""

    class Meta:
        model = PythonActionData
        fields = ActionDataSerializer.Meta.fields + [
            "code",
            "use_combobox",
            "combobox_code",
        ]
        read_only_fields = ActionDataSerializer.Meta.read_only_fields


class LinkActionDataSerializer(ActionDataSerializer):
    """Serializer for LinkActionData model."""

    class Meta:
        model = LinkActionData
        fields = ActionDataSerializer.Meta.fields + ["url"]
        read_only_fields = ActionDataSerializer.Meta.read_only_fields


class WindowsCMDActionDataSerializer(ActionDataSerializer):
    """Serializer for WindowsCMDActionData model."""

    class Meta:
        model = WindowsCMDActionData
        fields = ActionDataSerializer.Meta.fields + [
            "code",
            "use_combobox",
            "combobox_code",
        ]
        read_only_fields = ActionDataSerializer.Meta.read_only_fields


action_data_serializers = {
    PythonActionData.TYPE: PythonActionDataSerializer,
    LinkActionData.TYPE: LinkActionDataSerializer,
    WindowsCMDActionData.TYPE: WindowsCMDActionDataSerializer,
}
