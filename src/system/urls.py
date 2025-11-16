from django.urls import path
from .views import (
    SystemInfoView,
    SystemDefaultBackgroundView,
    system_default_background_file,
)

urlpatterns = [
    path("system-info", SystemInfoView.as_view(), name="system-info"),
    path("system-info/default-background", SystemDefaultBackgroundView.as_view()),
    path(
        "system-info/default-background/<str:filename>",
        system_default_background_file,
        name="system-default-background-file",
    ),
]
