from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from jumper.permissions import IsOwner, IsReadOnly
from users.permissions import IsAdmin
from users.models import User
from users.serializers.user_serializers import UserSerializer
from .user_profile_picture_mixin import UserProfilePictureMixin


class UserPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "limit"
    max_page_size = 1000


class UserViewSet(viewsets.ModelViewSet, UserProfilePictureMixin):
    """API endpoint that allows users to be viewed or edited."""

    queryset = User.objects.all()
    model = User
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = [
        "username",
        "is_superuser",
        "is_active",
        "creation_date",
    ]
    ordering = ["username"]
    permission_classes = [IsAuthenticated, IsReadOnly | IsOwner | IsAdmin]
    search_fields = ["username", "email", "first_name", "last_name"]
    filterset_fields = ["is_active", "is_superuser"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(methods=["get"], detail=False)
    def me(self, request: Request) -> Response:
        return Response(UserSerializer(request.user, context={"request": request}).data)

    @action(methods=["get"], detail=False)
    def exists(self, request: Request) -> Response:
        """Check if user exists with username, email or both."""
        username = request.query_params.get("username")
        email = request.query_params.get("email")
        if not username and not email:
            raise ValidationError("Username or email must be provided.")
        if username and email:
            return Response(
                User.objects.filter(username=username, email=email).exists()
            )
        if username:
            return Response(User.objects.filter(username=username).exists())
        return Response(User.objects.filter(email=email).exists())

    @action(
        detail=True,
        methods=["get"],
        url_name="is-last-admin",
        url_path="is-last-admin",
    )
    def is_last_admin(self, request: Request, pk=None) -> Response:
        """Check if the user is the last admin."""
        user = self.get_object()
        if user.is_superuser:
            return Response(
                User.objects.filter(is_superuser=True).exclude(pk=pk).count() == 0
            )
        return Response(False)
