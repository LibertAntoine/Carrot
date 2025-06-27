from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from jumper.permissions import IsReadOnly
from users.models import Group
from users.serializers.group_serializers import GroupSerializer, GroupDetailedSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter, SearchFilter

class GroupPagination(PageNumberPagination):
    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = settings.DEFAULT_PAGE_SIZE_QUERY_PARAM
    max_page_size = settings.DEFAULT_MAX_PAGE_SIZE


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all() if settings.SCIM_ENABLED else Group.objects.none()
    model = Group
    pagination_class = GroupPagination
    filter_backends = [OrderingFilter, SearchFilter]
    permission_classes = [IsAuthenticated, IsReadOnly]
    ordering_fields = [
        "name",
        "user_set",
        "is_admin_group",
    ]
    ordering = ["name"]
    search_fields = ["name"]

    def get_serializer_class(self):
        if self.request.query_params.get("detailed") == "true" and self.action in ['retrieve', 'list']:
            return GroupDetailedSerializer
        return GroupSerializer
