from rest_framework import viewsets
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from users.serializers.user_serializers import UserSerializer
from users.serializers.group_serializers import GroupDetailedSerializer
from users.serializers.role_serializers import RoleDetailedSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
from actions.models.action_models import Action
from users.models import User, Group, Role
from actions.serializers.action_data_version_serializers import (
    action_data_serializers
)
from actions.serializers.action_serializers import (
    ActionSerializer,
    ActionDetailedSerializer,
    ActionPlayableSerializer,
)
from rest_framework.pagination import PageNumberPagination
from .action_thumbnail_viewset import ActionThumbnailMixin


class ActionPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "limit"
    max_page_size = 1000


class ActionViewSet(viewsets.ModelViewSet, ActionThumbnailMixin):
    queryset = Action.objects.all()
    model = Action
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = ActionPagination
    ordering_fields = [
        "name",
        "creation_date",
        "last_update",
        "create_by",
    ]
    ordering = ["name"]
    search_fields = ["name", "description", "is_active", "is_public"]

    def get_serializer_class(self):
        if self.request.query_params.get("detailed") == "true":
            return ActionDetailedSerializer
        return ActionSerializer

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def mine(self, request):
        actions = self.get_user_active_actions(request.user)
        return Response(
            ActionPlayableSerializer(
                actions, many=True, context={"request": request}
            ).data
        )

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def search(self, request):
        search_term = request.query_params.get("query")
        limit = request.query_params.get("limit", 10)
        if not search_term:
            return Response({"error": "query param is required."}, status=400)
        terms = search_term.split()
        users_search_query = Q()
        groups_search_query = Q()
        roles_search_query = Q()
        for term in terms:
            users_search_query &= (
                Q(username__icontains=term)
                | Q(email__icontains=term)
                | Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
            )
            groups_search_query &= Q(name__icontains=term)
            roles_search_query &= Q(name__icontains=term) | Q(
                description__icontains=term
            )
        users = User.objects.filter(users_search_query).distinct()[:limit]
        groups = Group.objects.filter(groups_search_query).distinct()[:limit]
        roles = Role.objects.filter(roles_search_query).distinct()[:limit]

        user_serializer = UserSerializer(users, many=True)
        group_serializer = GroupDetailedSerializer(groups, many=True)
        role_serializer = RoleDetailedSerializer(roles, many=True)

        return Response(
            {
                "users": user_serializer.data,
                "groups": group_serializer.data,
                "roles": role_serializer.data,
            }
        )
    
    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    def versions(self, request, pk=None):
        action_obj = self.get_object()
        version_count = action_obj.data.history.count()

        versions = action_obj.data.history.order_by("-history_date")[:10]
        SerializerClass = action_data_serializers.get(
            action_obj.data.type
        )
        serializer = SerializerClass(versions, many=True)
        for version in serializer.data:
            if version.get("history"):
                version["history"]['number'] = version_count
            version_count -= 1
        return Response(serializer.data)

    def get_user_active_actions(self, user):
        queryset = (
            self.queryset.filter(is_active=True).filter(
                Q(users=user)  # Actions linked to user
                | Q(groups__user_set=user)  # Actions linked to user via group
                | Q(roles__users=user)  # Actions linked to user via role
                | Q(roles__groups__user_set=user)  # Actions linked to user via role group
                | Q(is_public=True)  # Actions marked as public
            )
            .distinct()
            .prefetch_related("users", "groups", "roles__users", "roles__groups")
        )

        return self.filter_queryset(queryset)

