from rest_framework import routers
from .views.action_viewset import ActionViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"actions", ActionViewSet, basename="actions")

urlpatterns = [*router.urls]
