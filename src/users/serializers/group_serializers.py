from rest_framework import serializers
from django.conf import settings

from users.models import Group

class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model."""

    is_admin_group = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "user_set",
            "is_admin_group",
        ]
        read_only_fields = ["id", "name", "user_set", "is_admin_group"]

    def get_is_admin_group(self, group: Group) -> bool:
        """Return True if group is admin group."""
        admin_group = Group.objects.filter(name=settings.ADMIN_GROUP).first()
        if not admin_group:
            return False
        return group.id == admin_group.id
