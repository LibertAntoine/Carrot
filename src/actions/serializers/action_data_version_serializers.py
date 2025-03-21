from rest_framework import serializers
from actions.models.action_data_models import PythonActionData, LinkActionData, ActionData


class ActionDataSerializer(serializers.ModelSerializer):
    """Serializer for ActionData model."""

    class Meta:
        abstract = True
        model = ActionData
        fields = ["id", "type"]
        read_only_fields = [
            "id", "type"
        ]


class PythonActionDataSerializer(ActionDataSerializer):
    """Serializer for PythonActionData model."""

    class Meta:
        model = PythonActionData
        fields = ActionDataSerializer.Meta.fields + ["id", "code"]
        read_only_fields = ActionDataSerializer.Meta.read_only_fields + [
            "id",
        ]


class LinkActionDataSerializer(ActionDataSerializer):
    """Serializer for LinkActionData model."""

    class Meta:
        model = LinkActionData
        fields = ActionDataSerializer.Meta.fields + ["id", "url"]
        read_only_fields = ActionDataSerializer.Meta.read_only_fields + [
            "id",
        ]


action_data_serializers = {
    PythonActionData.TYPE: PythonActionDataSerializer,
    LinkActionData.TYPE: LinkActionDataSerializer,
}
