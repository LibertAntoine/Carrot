from rest_framework import viewsets
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from rest_framework.filters import OrderingFilter, SearchFilter
from actions.models.action_models import Action
from actions.serializers.action_serializers import (
    ActionSerializer,
    ActionReadDetailedSerializer,
    ActionWriteDetailedSerializer,
    ActionPlayableSerializer
)
from rest_framework.pagination import PageNumberPagination


class ActionPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "limit"
    max_page_size = 1000


class ActionViewSet(viewsets.ModelViewSet):
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
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        if self.request.query_params.get("detailed") == "true":
            if self.request.method == "GET":
                return ActionReadDetailedSerializer
            return ActionWriteDetailedSerializer
        return ActionSerializer

    def perform_create(self, serializer):
        serializer.save(create_by=self.request.user)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def mine(self, request):
        actions = get_user_actions(request.user)
        return Response(
            ActionPlayableSerializer(actions, many=True).data
        )


def get_user_actions(user):
    return Action.objects.filter(
        Q(users=user) |  # Actions linked to user
        Q(groups__user_set=user) |  # Actions linked to user via group
        Q(roles__users=user) |  # Actions linked to user via role
        Q(roles__groups__user_set=user)  # Actions linked to user via role group
    ).distinct().prefetch_related(
        'users', 'groups', 'roles__users', 'roles__groups'
    )
