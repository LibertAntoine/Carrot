from django.urls import include, path, re_path
from .swagger import swagger_urls
from rest_framework import routers
from django.views.static import serve
from jumper import settings
from .front_updater import check_update

router = routers.DefaultRouter()

urlpatterns = [
    path("v1/", include([
        *router.urls,
        path("", include("users.urls")),
        path("", include("auths.urls")),
        path("", include("actions.urls")),
        path("", include("system.urls")),
        path("", include("workspaces.urls")),
        path("frontend-update", check_update, name="frontend-update"),
        # Documentation routes
        *swagger_urls
    ])),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]