"""
URL configuration for Law Mithra project.

Endpoints:
- /admin/ : Django Administration
- /api/health/ : Health Check endpoint
- /api/schema/ : OpenAPI 3 JSON/YAML Schema
- /api/docs/ : Swagger UI documentation (drf-spectacular)
- /api/redoc/ : ReDoc documentation (drf-spectacular)
"""

from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.conf import settings
from django.conf.urls.static import static
from config.views import HealthCheckView
from django.http import JsonResponse

urlpatterns = [
    # Root status check
    re_path(r'^/?$', lambda request: JsonResponse({
        'status': 'online',
        'service': 'Law Mithra API',
        'health': '/api/health/',
        'docs': '/api/docs/'
    })),

    # Administration
    re_path(r'^admin/?', admin.site.urls),

    # Health Check Endpoint (supports both with and without trailing slash)
    re_path(r'^api/health/?$', HealthCheckView.as_view(), name='api-health'),

    # Authentication & Profile
    re_path(r'^api/auth/', include('accounts.urls')),

    # Phase 1: Documents Vault & Extraction
    re_path(r'^api/documents/', include('documents.urls')),

    # Phase 2: Section Detection (nested under documents for ownership-filtered endpoints)
    re_path(r'^api/documents/(?P<doc_id>[0-9a-f-]+)/', include('analysis.urls')),

    # Multilingual Legal AI & Knowledge Services
    re_path(r'^api/knowledge/', include('knowledge.urls')),

    # OpenAPI 3 Schema & Swagger UI
    re_path(r'^api/schema/?$', SpectacularAPIView.as_view(), name='schema'),
    re_path(r'^api/docs/?$', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    re_path(r'^api/redoc/?$', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


