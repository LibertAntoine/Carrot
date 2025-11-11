from django.urls import path
from .views import SystemInfoView, SystemDefaultBackgroundView

urlpatterns = [
    path("system-info", SystemInfoView.as_view(), name="system-info"),
    path(
        "system-info/default-background",
        SystemDefaultBackgroundView.as_view(),
        name="system-default-background",
    ),
]