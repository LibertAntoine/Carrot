from rest_framework import serializers
from actions.models.action_data_models import (
    PythonActionData,
    LinkActionData,
    WindowsCMDActionData,
    ActionData,
)
from users.serializers.user_serializers import ShortUserSerializer
from users.models import User


class ActionDataSerializer(serializers.ModelSerializer):
    """Serializer for ActionData model."""

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if vars(instance).get("history_id", None):
            user_data = None
            if instance.history_user_id:
                try:
                    user = User.objects.get(pk=instance.history_user_id)
                    user_data = ShortUserSerializer(user, context=self.context).data
                except User.DoesNotExist:
                    user_data = None
            rep["history"] = {
                "id": instance.history_id,
                "user": user_data,
                "date": instance.history_date,
            }
        return rep

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
