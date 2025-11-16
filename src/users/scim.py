import re
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django_scim.adapters import SCIMUser as BaseSCIMUser, SCIMGroup as BaseSCIMGroup
from users.models import Group
from django.conf import settings
from django_scim.models import (
    SCIMServiceProviderConfig as DefaultSCIMServiceProviderConfig,
)


class SCIMUser(BaseSCIMUser):
    def from_dict(self, d):
        super().from_dict(d)
        # Custom logic to handle user creation
        self.obj.id = None
        self.obj.scim_id = None
        self.obj.email = self.obj.email.lower()
        self.obj = self._merge_if_user_exist(self.obj)
        self._manage_unique_username()

    def _merge_if_user_exist(self, obj):
        user = (
            get_user_model()
            .objects.filter(scim_external_id=self.obj.scim_external_id)
            .first()
        )
        if user:
            user.is_active = self.obj.is_active
            user.first_name = self.obj.first_name
            user.last_name = self.obj.last_name
            user.email = self.obj.email
            user.username = self.obj.username
            return user
        if settings.SCIM_ALLOW_USER_CREATION_CONFLIT:
            user = get_user_model().objects.filter(email=self.obj.email).first()
            if user:
                user.is_active = self.obj.is_active
                user.first_name = self.obj.first_name
                user.last_name = self.obj.last_name
                user.scim_external_id = self.obj.scim_external_id
                user.email = self.obj.email
                user.username = self.obj.username
                return user
        return obj

    def _manage_unique_username(self):
        while True:
            user_with_same_username = (
                get_user_model().objects.filter(username=self.obj.username).first()
            )
            if (
                not user_with_same_username
                or user_with_same_username.scim_external_id == self.obj.scim_external_id
            ):
                break
            # use regex to found if username finish with "_number"
            if re.search(r"_\d+$", self.obj.username):
                # if it's the case, increment the number
                self.obj.username = re.sub(
                    r"_(\d+)$",
                    lambda x: "_" + str(int(x.group(1)) + 1),
                    self.obj.username,
                )
            self.obj.username = self.obj.username + "_1"

    def delete(self):
        if not settings.SCIM_ALLOW_USER_DELETION:
            super().delete()
        else:
            self.obj.__class__.objects.filter(id=self.id).is_active = False
            self.save()


class SCIMGroup(BaseSCIMGroup):
    def from_dict(self, d):
        super().from_dict(d)
        self.obj.id = None
        self.obj.scim_id = None
        group = Group.objects.filter(scim_external_id=self.obj.scim_external_id).first()
        if group:
            group.name = self.obj.name
            self.obj = group
        else:
            group = Group.objects.filter(name=self.obj.name).first()
            if group:
                group.scim_external_id = self.obj.scim_external_id
                self.obj = group
        member_ids = [member["value"] for member in d.get("members", [])]
        users = get_user_model().objects.filter(id__in=member_ids)
        self.save()
        self.obj.user_set.set(users)


class SCIMServiceProviderConfig(DefaultSCIMServiceProviderConfig):
    def to_dict(self):
        d = super().to_dict()
        d["patch"]["supported"] = False
        return d


class SCIMAuthCheckMiddleware:
    """
    Middleware to check for SCIM Bearer Token in Authorization header.
    401 Unauthorized response is returned if the token is missing or invalid.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        authorisation = request.headers.get("Authorization")
        if authorisation != "Bearer " + settings.SCIM_BEARER_TOKEN:
            return HttpResponse("Unauthorized", status=401)

        response = self.get_response(request, *args, **kwargs)
        return response
