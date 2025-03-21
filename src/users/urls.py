from rest_framework import routers
from django.urls import path, include
from django.conf import settings
from .views import user_viewset, group_viewset, role_viewset

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", user_viewset.UserViewSet, basename="user")
router.register(r"groups", group_viewset.GroupViewSet, basename="group")
router.register(r"roles", role_viewset.RoleViewSet, basename="role")

urlpatterns = [*router.urls]

if settings.SCIM_ENABLED:
    urlpatterns += [path("scim/v2/", include("django_scim.urls", namespace="scim"))]
