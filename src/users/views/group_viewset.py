from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from jumper.permissions import IsReadOnly
from users.models import Group
from users.serializers.group_serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all() if settings.SCIM_ENABLED else Group.objects.none()
    model = Group
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsReadOnly]
