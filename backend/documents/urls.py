from django.urls import re_path
from .views import (
    DocumentListCreateView,
    DocumentDetailView,
    DocumentReprocessView,
    DocumentDownloadView,
)

urlpatterns = [
    re_path(r'^/?$', DocumentListCreateView.as_view(), name='document-list-create'),
    re_path(r'^upload/?$', DocumentListCreateView.as_view(), name='document-upload'),
    re_path(r'^(?P<pk>[0-9a-f-]+)/?$', DocumentDetailView.as_view(), name='document-detail'),
    re_path(r'^(?P<pk>[0-9a-f-]+)/download/?$', DocumentDownloadView.as_view(), name='document-download'),
    re_path(r'^(?P<pk>[0-9a-f-]+)/reprocess/?$', DocumentReprocessView.as_view(), name='document-reprocess'),
]
