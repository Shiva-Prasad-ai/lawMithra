"""
URL patterns for Legal Section Detection + Universal Complaint Analysis Report.
All mounted under /api/documents/<uuid:doc_id>/ via config/urls.py.
"""

from django.urls import re_path
from analysis.views import (
    DetectSectionsView,
    SectionListCreateView,
    SectionDetailView,
    GenerateReportView,
    ReportListView,
    ReportDetailView,
    ReportDownloadPDFView,
    LatestReportView,
)

urlpatterns = [
    # ── Section Detection ─────────────────────────────────────────────────────
    re_path(r'^detect-sections/?$', DetectSectionsView.as_view(), name='detect-sections'),
    re_path(r'^sections/?$', SectionListCreateView.as_view(), name='section-list-create'),
    re_path(r'^sections/(?P<section_id>[0-9a-f-]+)/?$', SectionDetailView.as_view(), name='section-detail'),

    # ── Universal Complaint Analysis Report ──────────────────────────────────
    # POST  → generate (creates new version)
    re_path(r'^generate-report/?$', GenerateReportView.as_view(), name='generate-report'),
    # GET   → list all versions
    re_path(r'^reports/?$', ReportListView.as_view(), name='report-list'),
    # GET   → latest completed version (shortcut)
    re_path(r'^reports/latest/?$', LatestReportView.as_view(), name='report-latest'),
    # GET   → specific version detail
    re_path(r'^reports/(?P<report_id>[0-9a-f-]+)/?$', ReportDetailView.as_view(), name='report-detail'),
    # GET   → download specific version as PDF
    re_path(r'^reports/(?P<report_id>[0-9a-f-]+)/pdf/?$', ReportDownloadPDFView.as_view(), name='report-pdf'),
]
