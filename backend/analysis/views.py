"""
Views for Legal Section Detection and Universal Complaint Analysis Report.
All endpoints are ownership-filtered: other users get 404, unauthenticated gets 401.
"""

import logging
from collections import OrderedDict
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from documents.models import Document, DocumentPage
from analysis.models import DetectedSection, ComplaintReport
from analysis.serializers import (
    DetectedSectionSerializer,
    DetectedSectionUpdateSerializer,
    ManualSectionCreateSerializer,
)
from analysis.services.section_detector import detect_sections_for_document
from analysis.services.report_generator import generate_report
from analysis.services.pdf_generator import generate_pdf

logger = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_owned_document(doc_id, user):
    """Return Document owned by user, or None."""
    try:
        return Document.objects.get(id=doc_id, owner=user)
    except Document.DoesNotExist:
        return None


def _report_to_dict(report: ComplaintReport) -> dict:
    """Serialize a ComplaintReport model instance to response dict."""
    return {
        "id": str(report.id),
        "report_id": report.report_id,
        "version": report.version,
        "language": report.language,
        "status": report.status,
        "document_title": report.document.title,
        "generated_date": report.generated_at.strftime("%d/%m/%Y %H:%M UTC"),
        "case_complaint_no": report.case_complaint_no,
        "complaint_type": report.complaint_type,
        "case_status": report.case_status,
        "parties_involved": report.parties_involved,
        "incident_date_place": report.incident_date_place,
        "complaint_summary": report.complaint_summary,
        "legal_provisions": report.legal_provisions,
        "evidence_available": report.evidence_available,
        "evidence_missing": report.evidence_missing,
        "complainant_side": report.complainant_side,
        "respondent_side": report.respondent_side,
        "persons_role": report.persons_role,
        "rights_next_steps": report.rights_next_steps,
        "advocate_questions": report.advocate_questions,
        "current_stage": report.current_stage,
        "last_updated_date": report.last_updated_date,
        "error_message": report.error_message,
        "updated_at": report.updated_at.strftime("%d/%m/%Y %H:%M UTC"),
    }


# ─── Section Detection Views ───────────────────────────────────────────────────

class DetectSectionsView(APIView):
    """POST /api/documents/<doc_id>/detect-sections/"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Run section detection on document",
        description=(
            "Re-runs deterministic rule-based section detection on all pages. "
            "Replaces old auto-detected results while preserving confirmed and manually added items."
        ),
        responses={
            200: DetectedSectionSerializer(many=True),
            404: OpenApiResponse(description="Document not found or not owned by user"),
        },
    )
    def post(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"event=section_detection.manual_trigger doc_id={doc_id} user_id={request.user.id}")
        sections = detect_sections_for_document(str(document.id))
        serializer = DetectedSectionSerializer(sections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SectionListCreateView(APIView):
    """
    GET  /api/documents/<doc_id>/sections/  → list grouped by act_key
    POST /api/documents/<doc_id>/sections/  → manually add a section
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List detected sections grouped by Act",
        responses={200: OpenApiResponse(description="Grouped section list")},
    )
    def get(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sections = DetectedSection.objects.filter(document=document).order_by('page_number', 'start_char')
        serializer = DetectedSectionSerializer(sections, many=True)

        groups: OrderedDict = OrderedDict()
        for section_data in serializer.data:
            key = section_data['act_key']
            if key not in groups:
                groups[key] = {'act_key': key, 'count': 0, 'sections': []}
            groups[key]['count'] += 1
            groups[key]['sections'].append(section_data)

        return Response({'total_count': sections.count(), 'groups': list(groups.values())})

    @extend_schema(
        summary="Manually add a section",
        request=ManualSectionCreateSerializer,
        responses={201: DetectedSectionSerializer, 400: OpenApiResponse(description="Invalid offsets"), 404: OpenApiResponse(description="Document not found")},
    )
    def post(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManualSectionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            page = document.pages.get(page_number=data['page_number'])
        except DocumentPage.DoesNotExist:
            return Response(
                {"detail": f"Page {data['page_number']} not found in this document."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_char = data['start_char']
        end_char = data['end_char']

        if start_char >= end_char or end_char > len(page.extracted_text):
            return Response(
                {"detail": "Invalid character offsets for this page's text."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        matched_text = page.extracted_text[start_char:end_char]
        section = DetectedSection.objects.create(
            document=document,
            page=page,
            page_number=data['page_number'],
            act_raw='',
            act_key=data.get('act_key', 'UNKNOWN'),
            section_number=data['section_number'],
            sub_clause=data.get('sub_clause', ''),
            matched_text=matched_text,
            start_char=start_char,
            end_char=end_char,
            detection_method=DetectedSection.DetectionMethod.MANUAL,
            review_status=DetectedSection.ReviewStatus.AUTO,
        )

        logger.info(f"event=section.manual_add doc_id={doc_id} section_id={section.id} user_id={request.user.id}")
        return Response(DetectedSectionSerializer(section).data, status=status.HTTP_201_CREATED)


class SectionDetailView(APIView):
    """
    PATCH  /api/documents/<doc_id>/sections/<section_id>/  → confirm/reject or edit
    DELETE /api/documents/<doc_id>/sections/<section_id>/  → delete manual items only
    """
    permission_classes = [IsAuthenticated]

    def _get_section(self, doc_id, section_id, user):
        document = _get_owned_document(doc_id, user)
        if not document:
            return None, None
        try:
            section = DetectedSection.objects.get(id=section_id, document=document)
            return document, section
        except DetectedSection.DoesNotExist:
            return document, None

    @extend_schema(
        summary="Update section (confirm/reject/edit)",
        request=DetectedSectionUpdateSerializer,
        responses={200: DetectedSectionSerializer, 404: OpenApiResponse(description="Not found")},
    )
    def patch(self, request, doc_id, section_id):
        document, section = self._get_section(doc_id, section_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if not section:
            return Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DetectedSectionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields = ['updated_at']
        if 'review_status' in data:
            section.review_status = data['review_status']
            update_fields.append('review_status')
        if 'act_key' in data:
            section.act_key = data['act_key']
            update_fields.append('act_key')
        if 'section_number' in data:
            section.section_number = data['section_number']
            update_fields.append('section_number')

        section.save(update_fields=update_fields)
        logger.info(f"event=section.updated doc_id={doc_id} section_id={section_id} user_id={request.user.id}")
        return Response(DetectedSectionSerializer(section).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a manually added section",
        responses={204: OpenApiResponse(description="Deleted"), 400: OpenApiResponse(description="Only manual sections can be deleted"), 404: OpenApiResponse(description="Not found")},
    )
    def delete(self, request, doc_id, section_id):
        document, section = self._get_section(doc_id, section_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if not section:
            return Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

        if section.detection_method != DetectedSection.DetectionMethod.MANUAL:
            return Response(
                {"detail": "Only manually added sections can be deleted. Use reject to dismiss auto-detected sections."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        section_id_str = str(section.id)
        section.delete()
        logger.info(f"event=section.deleted doc_id={doc_id} section_id={section_id_str} user_id={request.user.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Universal Complaint Report Views ─────────────────────────────────────────

class GenerateReportView(APIView):
    """
    POST /api/documents/<doc_id>/generate-report/
    Generates (or regenerates) a Universal Complaint Analysis Report.
    Saves a new versioned record — never overwrites existing reports.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generate Universal Complaint Analysis Report",
        description=(
            "Analyses the document's extracted OCR text with Gemini AI and returns a structured "
            "7-section Universal Complaint Analysis Report. "
            "Each call creates a new versioned report record. "
            "Missing information is marked 'Not provided' or 'Requires verification'. "
            "Never assigns guilt or invents facts."
        ),
        responses={
            200: OpenApiResponse(description="Report JSON with all 7 sections"),
            404: OpenApiResponse(description="Document not found or not owned by user"),
            422: OpenApiResponse(description="Document has no extracted text yet"),
        },
    )
    def post(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Build full text from all OCR pages
        pages = document.pages.order_by('page_number')
        full_text = "\n\n".join(
            f"[Page {p.page_number}]\n{p.extracted_text}"
            for p in pages
            if p.extracted_text
        ).strip()

        if not full_text:
            return Response(
                {"detail": "Document has no extracted text. Please wait for OCR processing to complete or re-process."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        language = "en"
        if request.data:
            language = request.data.get("language", "en")

        # Determine next version number for this document
        last_version = ComplaintReport.objects.filter(
            document=document, owner=request.user
        ).order_by('-version').values_list('version', flat=True).first()
        next_version = (last_version or 0) + 1

        logger.info(f"event=report.generate doc_id={doc_id} user_id={request.user.id} lang={language} version={next_version}")

        # Create a placeholder DB record immediately
        report_record = ComplaintReport.objects.create(
            document=document,
            owner=request.user,
            report_id=f"LM-{str(doc_id)[:8].upper()}",
            version=next_version,
            language=language,
            status=ComplaintReport.ReportStatus.GENERATING,
        )

        try:
            report_data = generate_report(
                document_text=full_text,
                language=language,
                document_id=str(doc_id),
            )

            # Persist all 7 sections into DB
            report_record.report_id        = report_data["report_id"]
            report_record.status           = ComplaintReport.ReportStatus.COMPLETED
            report_record.complaint_type   = report_data.get("complaint_type", "")
            report_record.case_complaint_no= report_data.get("case_complaint_no", "")
            report_record.case_status      = report_data.get("status", "")
            report_record.parties_involved = report_data.get("parties_involved", "")
            report_record.incident_date_place = report_data.get("incident_date_place", "")
            report_record.complaint_summary= report_data.get("complaint_summary", "")
            report_record.legal_provisions = report_data.get("legal_provisions", [])
            report_record.evidence_available = report_data.get("evidence_available", [])
            report_record.evidence_missing = report_data.get("evidence_missing", [])
            report_record.complainant_side = report_data.get("complainant_side", "")
            report_record.respondent_side  = report_data.get("respondent_side", "")
            report_record.persons_role     = report_data.get("persons_role", "")
            report_record.rights_next_steps= report_data.get("rights_next_steps", "")
            report_record.advocate_questions = report_data.get("advocate_questions", "")
            report_record.current_stage    = report_data.get("current_stage", "")
            report_record.last_updated_date= report_data.get("last_updated_date", "")
            report_record.save()

        except Exception as exc:
            report_record.status = ComplaintReport.ReportStatus.FAILED
            report_record.error_message = str(exc)
            report_record.save()
            logger.error(f"event=report.error doc_id={doc_id} error={exc}")
            return Response(
                {"detail": f"Report generation failed: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(_report_to_dict(report_record), status=status.HTTP_200_OK)


class ReportListView(APIView):
    """
    GET /api/documents/<doc_id>/reports/
    Returns all report versions for a document, newest first.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all report versions for a document",
        responses={200: OpenApiResponse(description="List of report versions")},
    )
    def get(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        reports = ComplaintReport.objects.filter(
            document=document, owner=request.user
        ).order_by('-version')

        return Response({
            "count": reports.count(),
            "reports": [_report_to_dict(r) for r in reports],
        })


class ReportDetailView(APIView):
    """
    GET /api/documents/<doc_id>/reports/<report_db_id>/
    Retrieve one specific report version.
    """
    permission_classes = [IsAuthenticated]

    def _get_report(self, doc_id, report_id, user):
        document = _get_owned_document(doc_id, user)
        if not document:
            return None, None
        try:
            report = ComplaintReport.objects.get(id=report_id, document=document, owner=user)
            return document, report
        except ComplaintReport.DoesNotExist:
            return document, None

    @extend_schema(
        summary="Retrieve a specific report version",
        responses={200: OpenApiResponse(description="Report detail JSON"), 404: OpenApiResponse(description="Not found")},
    )
    def get(self, request, doc_id, report_id):
        document, report = self._get_report(doc_id, report_id, request.user)
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        if not report:
            return Response({"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(_report_to_dict(report))


class ReportDownloadPDFView(APIView):
    """
    GET /api/documents/<doc_id>/reports/<report_db_id>/pdf/
    Download the report as a professional A4 PDF.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Download report as PDF",
        responses={
            200: OpenApiResponse(description="PDF binary (application/pdf)"),
            404: OpenApiResponse(description="Report not found"),
        },
    )
    def get(self, request, doc_id, report_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            report = ComplaintReport.objects.get(id=report_id, document=document, owner=request.user)
        except ComplaintReport.DoesNotExist:
            return Response({"detail": "Report not found."}, status=status.HTTP_404_NOT_FOUND)

        if report.status != ComplaintReport.ReportStatus.COMPLETED:
            return Response(
                {"detail": "Report is not yet completed or failed to generate."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        try:
            pdf_bytes = generate_pdf(_report_to_dict(report))
        except Exception as exc:
            logger.error(f"event=pdf.error report_id={report_id} error={exc}")
            return Response(
                {"detail": f"PDF generation failed: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        safe_title = report.document.title.replace(' ', '_')[:40]
        filename = f"LawMithra_{safe_title}_{report.report_id}_v{report.version}.pdf"

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_bytes)
        return response


class LatestReportView(APIView):
    """
    GET /api/documents/<doc_id>/reports/latest/
    Returns the latest completed report for a document (or 404 if none).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get latest completed report for a document",
        responses={200: OpenApiResponse(description="Latest report JSON"), 404: OpenApiResponse(description="No report found")},
    )
    def get(self, request, doc_id):
        document = _get_owned_document(doc_id, request.user)
        if not document:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        report = ComplaintReport.objects.filter(
            document=document,
            owner=request.user,
            status=ComplaintReport.ReportStatus.COMPLETED,
        ).order_by('-version').first()

        if not report:
            return Response({"detail": "No completed report found for this document."}, status=status.HTTP_404_NOT_FOUND)

        return Response(_report_to_dict(report))
