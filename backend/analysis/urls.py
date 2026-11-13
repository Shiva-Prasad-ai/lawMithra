"""
URL patterns for Legal Section Detection + Universal Complaint Analysis Report.
All mounted under /api/documents/<uuid:doc_id>/ via config/urls.py.
"""

from django.urls import path
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
    path('detect-sections/', DetectSectionsView.as_view(), name='detect-sections'),
    path('sections/', SectionListCreateView.as_view(), name='section-list-create'),
    path('sections/<uuid:section_id>/', SectionDetailView.as_view(), name='section-detail'),

    # ── Universal Complaint Analysis Report ──────────────────────────────────
    # POST  → generate (creates new version)
    path('generate-report/', GenerateReportView.as_view(), name='generate-report'),
    # GET   → list all versions
    path('reports/', ReportListView.as_view(), name='report-list'),
    # GET   → latest completed version (shortcut)
    path('reports/latest/', LatestReportView.as_view(), name='report-latest'),
    # GET   → specific version detail
    path('reports/<uuid:report_id>/', ReportDetailView.as_view(), name='report-detail'),
    # GET   → download specific version as PDF
    path('reports/<uuid:report_id>/pdf/', ReportDownloadPDFView.as_view(), name='report-pdf'),
]
