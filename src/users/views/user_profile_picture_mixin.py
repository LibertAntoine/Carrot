from http import HTTPMethod
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.serializers.user_serializers import UserProfilePictureSerializer
from django.http import HttpResponse
from django.urls import reverse


class UserProfilePictureMixin:
    @action(
        detail=True,
        methods=[HTTPMethod.GET],
        url_name="profile",
        url_path=r"profile/(?P<filename>[\w\-\.]+)",
    )
    def profile_picture(self, request, pk=None, filename=None):
        """Update user profile picture."""
        user = self.get_object()
        if not user.profile_picture:
            return Response("No profile picture.", status=status.HTTP_404_NOT_FOUND)
        return HttpResponse(user.profile_picture, content_type="image/png")

    @action(
        detail=True,
        methods=[HTTPMethod.PUT],
        url_name="profile",
        url_path="profile",
    )
    def set_profile_picture(self, request, pk=None):
        """Update user profile picture."""
        serializer = UserProfilePictureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.profile_picture = serializer.validated_data["profile_picture"]
        user.save()
        file_name = user.profile_picture.name.split("/")[-1]
        return Response(
            {
                "profile_picture_url": request.build_absolute_uri(
                    reverse("user-profile", args=[user.id, file_name])
                )
            }
        )
