"""
PDF Generation Service for Law Mithra Universal Complaint Analysis Report.
Generates a professional A4 one-page PDF using ReportLab.
"""

import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.platypus.flowables import KeepTogether


# ── Colour palette ─────────────────────────────────────────────────────────────
DARK_NAVY  = colors.HexColor('#1A2E4C')
STEEL_BLUE = colors.HexColor('#2C4C6E')
LIGHT_BLUE = colors.HexColor('#EBF1F8')
MID_BLUE   = colors.HexColor('#C8D8E9')
BORDER     = colors.HexColor('#B8C8DB')
WHITE      = colors.white
BLACK      = colors.HexColor('#111111')
GREY       = colors.HexColor('#4A5568')
LIGHT_GREY = colors.HexColor('#F5F7FA')
AMBER      = colors.HexColor('#B91C1C')
ROW_EVEN   = colors.HexColor('#F8FAFD')
ROW_ODD    = colors.white


def _style(name, **kwargs):
    """Create a named ParagraphStyle with given kwargs."""
    return ParagraphStyle(name=name, **kwargs)


def _truncate(text: str, max_chars: int = 400) -> str:
    """Truncate long text to fit PDF; append ellipsis."""
    if not text or text in ('Not provided', 'Requires verification', 'Not Applicable'):
        return text or 'Not provided'
    text = str(text).strip()
    if len(text) > max_chars:
        return text[:max_chars - 3] + '...'
    return text


def _list_items(items: List[str], bullet: str = '•', max_items: int = 6) -> str:
    """Convert list to bullet-separated inline string for PDF cell."""
    if not items:
        return 'Not provided'
    shown = items[:max_items]
    result = '<br/>'.join(f'{bullet} {_truncate(i, 160)}' for i in shown)
    if len(items) > max_items:
        result += f'<br/>... and {len(items) - max_items} more'
    return result


def generate_pdf(report_data: Dict[str, Any]) -> bytes:
    """
    Generate a professional A4 PDF for the Universal Complaint Analysis Report.
    Returns raw PDF bytes.
    """
    buf = io.BytesIO()
    PAGE_W, PAGE_H = A4   # 595.27 x 841.89 points
    MARGIN = 10 * mm

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title=f"Law Mithra – {report_data.get('report_id', 'Report')}",
        author='Law Mithra AI Legal Assistant',
        subject='Universal Complaint Analysis Report',
    )

    CONTENT_W = PAGE_W - 2 * MARGIN

    # ── Styles ────────────────────────────────────────────────────────────────
    brand_style   = _style('Brand',   fontName='Helvetica-Bold',  fontSize=13, textColor=DARK_NAVY,  alignment=TA_CENTER, spaceAfter=1)
    tagline_style = _style('Tagline', fontName='Helvetica',        fontSize=6.5, textColor=STEEL_BLUE, alignment=TA_CENTER, spaceAfter=4, letterSpacing=0.5)

    sec_style   = _style('Sec',  fontName='Helvetica-Bold',  fontSize=7.5, textColor=DARK_NAVY,  spaceAfter=1.5, spaceBefore=3)
    hdr_style   = _style('Hdr',  fontName='Helvetica-Bold',  fontSize=6.5, textColor=DARK_NAVY,  spaceAfter=0)
    cell_style  = _style('Cell', fontName='Helvetica',        fontSize=6.5, textColor=BLACK,      spaceAfter=0, leading=8.5)
    italic_cell = _style('Ital', fontName='Helvetica-Oblique',fontSize=6.0, textColor=GREY,       spaceAfter=0, leading=8.0)
    body_style  = _style('Body', fontName='Helvetica',        fontSize=6.5, textColor=BLACK,      leading=8.5,    spaceAfter=0, alignment=TA_JUSTIFY)
    disc_style  = _style('Disc', fontName='Helvetica',        fontSize=5.5, textColor=AMBER,      leading=7.5,    spaceAfter=0, alignment=TA_JUSTIFY)
    conf_style  = _style('Conf', fontName='Helvetica-Oblique',fontSize=5.0, textColor=GREY,       leading=6.5,    spaceAfter=0, alignment=TA_CENTER)

    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    story.append(Paragraph('LAW MITHRA', brand_style))
    story.append(Paragraph('YOUR SMART LEGAL ASSISTANT &nbsp;|&nbsp; UNIVERSAL COMPLAINT REPORT', tagline_style))

    def section_label(number: str, title: str):
        """Return a clean section title matching the Law Mithra report template."""
        return Paragraph(f'{number}. {title}', sec_style)

    def mini_table(headers: List[str], rows: List[List[str]], col_w: List[float]):
        """Build a compact bordered table with header row."""
        data = [[Paragraph(h, hdr_style) for h in headers]]
        for i, row in enumerate(rows):
            st = italic_cell if any(v in ('Not provided', 'Requires verification', 'Not Applicable') for v in row) else cell_style
            data.append([Paragraph(str(v), st) for v in row])

        ts = TableStyle([
            # Header
            ('BACKGROUND',    (0,0), (-1,0),  LIGHT_BLUE),
            ('TEXTCOLOR',     (0,0), (-1,0),  DARK_NAVY),
            ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,-1), 6.5),
            # Alternating rows
            *[('BACKGROUND', (0,i), (-1,i), ROW_EVEN if i % 2 == 0 else ROW_ODD)
              for i in range(1, len(data))],
            # Grid
            ('GRID', (0,0), (-1,-1), 0.4, BORDER),
            # Padding
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
        return Table(data, colWidths=col_w, style=ts, repeatRows=1)

    # ── TOP IDENTITY ROW ──────────────────────────────────────────────────────
    id_data = [
        [Paragraph('REPORT ID', hdr_style),
         Paragraph('CASE / COMPLAINT NO.', hdr_style),
         Paragraph('GENERATED DATE', hdr_style),
         Paragraph('STATUS', hdr_style)],
        [Paragraph(report_data.get('report_id', ''), cell_style),
         Paragraph(_truncate(report_data.get('case_complaint_no', 'Not provided'), 60), cell_style),
         Paragraph(report_data.get('generated_date', ''), cell_style),
         Paragraph(_truncate(report_data.get('status', 'Not provided'), 60), cell_style)],
    ]
    id_table = Table(
        id_data,
        colWidths=[CONTENT_W * 0.18, CONTENT_W * 0.30, CONTENT_W * 0.25, CONTENT_W * 0.27],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(id_table)
    story.append(Spacer(1, 2))

    # ── SECTION 1: CASE AT A GLANCE ──────────────────────────────────────────
    story.append(section_label('1', 'CASE AT A GLANCE'))
    glance_data = [
        [Paragraph('COMPLAINT TYPE / SUBJECT', hdr_style),
         Paragraph('PARTIES INVOLVED', hdr_style),
         Paragraph('DATE & PLACE', hdr_style)],
        [Paragraph(_truncate(report_data.get('complaint_type','Not provided'), 100), cell_style),
         Paragraph(_truncate(report_data.get('parties_involved','Not provided'), 160), cell_style),
         Paragraph(_truncate(report_data.get('incident_date_place','Not provided'), 100), cell_style)],
    ]
    glance_table = Table(
        glance_data,
        colWidths=[CONTENT_W * 0.28, CONTENT_W * 0.42, CONTENT_W * 0.30],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(glance_table)
    story.append(Spacer(1, 2))

    # ── SECTION 2: COMPLAINT SUMMARY ─────────────────────────────────────────
    story.append(section_label('2', 'COMPLAINT SUMMARY'))
    summary_intro = (
        'Neutral summary of what the complaint/document says: what allegedly happened, who is involved, '
        'when and where it happened, the impact claimed, and what action or relief is requested. '
        'Separate reported claims from independently verified facts.'
    )
    summary_data = [
        [Paragraph(summary_intro, italic_cell)],
        [Paragraph('AI-GENERATED CASE SUMMARY (POPULATED FROM UPLOADED DOCUMENT)', hdr_style)],
        [Paragraph(_truncate(report_data.get('complaint_summary', 'Requires verification'), 500), body_style)],
    ]
    summary_table = Table(
        summary_data,
        colWidths=[CONTENT_W],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (0,0), LIGHT_GREY),
            ('BACKGROUND',    (0,1), (0,1), LIGHT_BLUE),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 5),
            ('RIGHTPADDING',  (0,0), (-1,-1), 5),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 2))

    # ── SECTION 3: POSSIBLE LEGAL PROVISIONS ─────────────────────────────────
    story.append(section_label('3', 'POSSIBLE LEGAL PROVISIONS'))
    prov_headers = ['ACT / SECTION', 'WHY IT MAY BE RELEVANT', 'VERIFICATION / CAVEAT']
    prov_col_w   = [CONTENT_W * 0.22, CONTENT_W * 0.42, CONTENT_W * 0.36]
    provisions   = report_data.get('legal_provisions', [])
    prov_rows    = []
    for p in provisions[:4]:   # max 4 provisions to stay on one page
        prov_rows.append([
            _truncate(p.get('act_section', 'Requires verification'), 80),
            _truncate(p.get('relevance',   'Requires verification'), 180),
            _truncate(p.get('caveat',      'Check ingredients, date, amendments and jurisdiction.'), 160),
        ])
    if not prov_rows:
        prov_rows = [['Requires verification', 'Requires verification',
                      'Check ingredients, date, amendments and jurisdiction. Do not treat a possible section as a final finding.']]
    story.append(mini_table(prov_headers, prov_rows, prov_col_w))
    story.append(Spacer(1, 2))

    # ── SECTION 4: KEY EVIDENCE & DOCUMENTS ──────────────────────────────────
    story.append(section_label('4', 'KEY EVIDENCE & DOCUMENTS'))
    avail_text   = _list_items(report_data.get('evidence_available', ['Not provided']), '✓')
    missing_text = _list_items(report_data.get('evidence_missing',   ['Requires verification']), '✗')
    evid_data = [
        [Paragraph('AVAILABLE MATERIAL', hdr_style),
         Paragraph('MISSING / TO BE VERIFIED', hdr_style)],
        [Paragraph(avail_text,   cell_style),
         Paragraph(missing_text, cell_style)],
    ]
    evid_table = Table(
        evid_data,
        colWidths=[CONTENT_W * 0.5, CONTENT_W * 0.5],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(evid_table)
    story.append(Spacer(1, 2))

    # ── SECTION 5: BALANCED CASE VIEW ────────────────────────────────────────
    story.append(section_label('5', 'BALANCED CASE VIEW'))
    balanced_data = [
        [Paragraph('COMPLAINANT / APPLICANT SIDE', hdr_style),
         Paragraph('RESPONDENT / ACCUSED / OTHER SIDE', hdr_style)],
        [Paragraph(_truncate(report_data.get('complainant_side', 'Requires verification'), 300), cell_style),
         Paragraph(_truncate(report_data.get('respondent_side',  'Requires verification'), 300), cell_style)],
    ]
    balanced_note = [
        [Paragraph(
            'Claim, supporting material, requested remedy and gaps to clarify.',
            italic_cell
        ),
         Paragraph(
            'Known response, relevant rights, possible issues or defences for advocate review. '
            'Do not presume guilt or liability.',
            italic_cell
        )],
    ]
    balanced_table = Table(
        balanced_data + balanced_note,
        colWidths=[CONTENT_W * 0.5, CONTENT_W * 0.5],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('BACKGROUND',    (0,2), (-1,2), LIGHT_GREY),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(balanced_table)
    story.append(Spacer(1, 2))

    # ── SECTION 6: RIGHTS & NEXT STEPS ───────────────────────────────────────
    story.append(section_label('6', 'RIGHTS & NEXT STEPS'))
    rights_data = [
        [Paragraph("PERSON'S ROLE", hdr_style),
         Paragraph('PRACTICAL NEXT STEPS / DEADLINES', hdr_style)],
        [Paragraph(_truncate(report_data.get('persons_role',      'Requires verification'), 120), cell_style),
         Paragraph(_truncate(report_data.get('rights_next_steps', 'Requires verification'), 350), cell_style)],
        [Paragraph(
            'Complainant / accused / respondent / witness / other: identify from user or mark unknown.',
            italic_cell
         ),
         Paragraph(
            'Role-specific general options, documents to preserve, authority to contact, notices or '
            'deadlines to check, and when to consult an advocate.',
            italic_cell
         )],
    ]
    rights_table = Table(
        rights_data,
        colWidths=[CONTENT_W * 0.28, CONTENT_W * 0.72],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('BACKGROUND',    (0,2), (-1,2), LIGHT_GREY),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(rights_table)
    story.append(Spacer(1, 2))

    # ── SECTION 7: ADVOCATE REVIEW / CASE STATUS ─────────────────────────────
    story.append(section_label('7', 'ADVOCATE REVIEW / CASE STATUS'))
    adv_data = [
        [Paragraph('QUESTIONS FOR ADVOCATE', hdr_style),
         Paragraph('CURRENT STAGE & NEXT ACTION', hdr_style),
         Paragraph('LAST UPDATED', hdr_style)],
        [Paragraph(_truncate(report_data.get('advocate_questions', 'Requires verification'), 250), cell_style),
         Paragraph(
            f"{_truncate(report_data.get('current_stage','Requires verification'), 150)}\n"
            "Intake / police / investigation / notice / court / appeal / other:",
            cell_style
         ),
         Paragraph(
            f"Date: {_truncate(report_data.get('last_updated_date', 'Requires verification'), 60)}\n"
            f"Version: {report_data.get('version', 1)}",
            cell_style
         )],
        [Paragraph(
            'Applicable law, jurisdiction, evidence, procedure, risks, remedies and missing facts to verify.',
            italic_cell
         ),
         Paragraph('', italic_cell),
         Paragraph('', italic_cell)],
    ]
    adv_table = Table(
        adv_data,
        colWidths=[CONTENT_W * 0.42, CONTENT_W * 0.37, CONTENT_W * 0.21],
        style=TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), LIGHT_BLUE),
            ('BACKGROUND',    (0,2), (-1,2), LIGHT_GREY),
            ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING',   (0,0), (-1,-1), 4),
            ('RIGHTPADDING',  (0,0), (-1,-1), 4),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ])
    )
    story.append(adv_table)
    story.append(Spacer(1, 3))

    # ── DISCLAIMER & CONFIDENTIALITY ─────────────────────────────────────────
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5, color=BORDER, spaceBefore=0, spaceAfter=2))
    disc_text = (
        '<b>IMPORTANT:</b> AI-assisted information only; not a police finding, court decision or '
        'substitute for a qualified advocate. Allegations are not proven facts. Legal provisions '
        'and deadlines must be verified against authoritative, current sources and the incident '
        'date. If information is missing or uncertain, display "Unknown / Needs verification" — '
        'never invent details.'
    )
    story.append(Paragraph(disc_text, disc_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        'CONFIDENTIAL — Contains personal and potentially sensitive case information. '
        'Share only with authorised people.',
        conf_style
    ))

    doc.build(story)
    return buf.getvalue()

