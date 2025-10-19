from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from django.db.models import Q
from jumper.permissions import IsReadOnly
from users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from users.permissions import IsActionManager
from .models import Workspace
from system.models import SystemInfo
from .serializers import WorkspaceSerializer, DetailedWorkspaceSerializer


class WorkspacePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "limit"
    max_page_size = 1000


class WorkspaceViewSet(viewsets.ModelViewSet):
    model = Workspace
    pagination_class = WorkspacePagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = [
        "name",
        "description",
        "created_at",
        "updated_at",
        "created_by",
        "is_active",
    ]
    ordering = ["name"]
    permission_classes = [
        IsAuthenticated,
        IsReadOnly | IsActionManager,
    ]
    search_fields = ["name", "description"]
    filterset_fields = ["name", "created_by", "is_active"]

    def get_queryset(self):
        if not SystemInfo.get_instance().allow_action_workspaces:
            return Workspace.objects.none()
        if not self.request.user.is_admin:
            return self.get_user_workspaces(Workspace.objects.all())
        return Workspace.objects.all()

    def get_permissions(self):
        if self.request.method in ("POST"):
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated, IsActionManager]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.query_params.get("detail") == "true":
            return DetailedWorkspaceSerializer
        return WorkspaceSerializer

    def get_user_workspaces(self, queryset):
        user = self.request.user
        workspace_ids = Workspace.objects.filter(
            Q(users=user)
            | Q(groups__user_set=user)
            | Q(roles__users=user)
            | Q(roles__groups__user_set=user)
        ).values_list("id", flat=True).distinct()
        return queryset.filter(id__in=workspace_ids).select_related("created_by")