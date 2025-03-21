from rest_framework import routers
from .views import ActionViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"actions", ActionViewSet, basename="actions")

urlpatterns = [*router.urls]
