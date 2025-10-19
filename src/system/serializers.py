from rest_framework import serializers
from .models import SystemInfo

class SystemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemInfo
        fields = [
            "allow_action_workspaces",
        ]
