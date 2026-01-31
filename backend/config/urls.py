"""
URL configuration for MonkeyUI backend.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse, FileResponse, Http404
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import os


def serve_media(request, path):
    """Serve media files in production when using local storage."""
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))
    raise Http404("Media file not found")


def health_check(request):
    """Health check endpoint for Fly.io and load balancers."""
    return JsonResponse({"status": "healthy", "service": "monkeyui-backend"})


urlpatterns = [
    # Health check (must be before catch-all)
    path('api/health/', health_check, name='health-check'),
    
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('api/accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('api/', include('apps.core.urls')),
    path('api/design-system/', include('apps.design_system.urls', namespace='design_system')),
    # API v1 endpoints
    path('api/v1/design-systems/', include('apps.design_system.urls', namespace='design_system_v1')),
]

# Serve media files when using local storage
# For S3/cloud storage, files are served directly from the storage provider
if settings.FILE_STORAGE_BACKEND == 'local':
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='serve-media'),
    ]
