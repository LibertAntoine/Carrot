from django.db.models import Count
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from rest_framework.filters import OrderingFilter, SearchFilter
from users.models import Role
from users.serializers.role_serializers import RoleSerializer, RoleDetailedSerializer
from rest_framework.pagination import PageNumberPagination


class RolePagination(PageNumberPagination):
    page_size = settings.DEFAULT_PAGE_SIZE
    page_size_query_param = settings.DEFAULT_PAGE_SIZE_QUERY_PARAM
    max_page_size = settings.DEFAULT_MAX_PAGE_SIZE


class RoleViewSet(viewsets.ModelViewSet):
    model = Role
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = RolePagination
    ordering_fields = [
        "name",
        "user_count",
        "group_count",
        "action_count",
        "creation_date",
        "last_update",
        "create_by",
    ]
    ordering = ["name"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = Role.objects.all()
        ordering = self.request.query_params.get("ordering", None)
        if ordering:
            if "user_count" in ordering:
                queryset = queryset.annotate(user_count=Count("users"))
            elif "group_count" in ordering:
                queryset = queryset.annotate(group_count=Count("groups"))
            elif "action_count" in ordering:
                queryset = queryset.annotate(action_count=Count("actions"))
        return queryset

    def get_serializer_class(self):
        if self.request.query_params.get("detailed") == "true":
            return RoleDetailedSerializer
        return RoleSerializer

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)
