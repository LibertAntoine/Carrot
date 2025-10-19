from rest_framework import routers
from .views import WorkspaceViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"workspaces", WorkspaceViewSet, basename="workspaces")

urlpatterns = [*router.urls]