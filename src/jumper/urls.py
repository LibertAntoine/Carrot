from django.urls import include, path, re_path
from .services.swagger import swagger_urls
from rest_framework import routers
from django.views.static import serve
from jumper import settings
from .views.front_updater_views import check_update
from .views.app_info_views import get_app_info

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("", get_app_info, name="app-info"),
    path("v1/", get_app_info, name="app-info"),
    path("v1/", include([
        *router.urls,
        path("", get_app_info, name="app-info"),
        path("frontend-update", check_update, name="frontend-update"),
        path("", include("users.urls")),
        path("", include("auths.urls")),
        path("", include("actions.urls")),
        path("", include("system.urls")),
        path("", include("workspaces.urls")),
        # Documentation routes
        *swagger_urls
    ])),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]