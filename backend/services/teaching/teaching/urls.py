from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .metrics_views import metrics

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(authentication_classes=[], permission_classes=[]),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema", authentication_classes=[], permission_classes=[]
        ),
        name="swagger-ui",
    ),
    path("api/", include("teaching.api_urls")),
    path("metrics", metrics),
]
