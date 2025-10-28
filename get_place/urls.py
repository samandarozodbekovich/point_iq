
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Share API",
        default_version='v1',
        description="Get place project",
        terms_of_service='getplace.com',
        contact=openapi.Contact(email="nosirovsamandar110@gmail.com"),
        license=openapi.License(name="getplace licence")
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('map/', include('apps.areas.urls')),
    path('users/', include('apps.users.urls')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
