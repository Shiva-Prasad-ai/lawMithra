import json
import pytest
from django.contrib.auth.models import User
from documents.models import Document, DocumentPage
from analysis.models import ComplaintReport


@pytest.mark.django_db
def test_complaint_report_workflow(client):
    # 1. Create user and log in
    user = User.objects.create_user(
        username="reportuser@lawmithra.in",
        email="reportuser@lawmithra.in",
        password="TestPassword@123"
    )
    login_resp = client.post(
        "/api/auth/login/",
        data={"email": "reportuser@lawmithra.in", "password": "TestPassword@123"},
        content_type="application/json"
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access"]
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    # 2. Create document with extracted text
    doc = Document.objects.create(
        owner=user,
        title="Cybercrime_Complaint.pdf",
        file_type="application/pdf",
        file_size=20480,
        status="completed"
    )
    DocumentPage.objects.create(
        document=doc,
        page_number=1,
        extracted_text=(
            "To the Cyber Crime Police Station, Bengaluru. "
            "Subject: Complaint regarding unauthorized credit card transaction of Rs. 45,000 on 10/10/2024. "
            "Sir, I received an SMS that money was debited from my account without my OTP. "
            "Please register an FIR under Section 66C and 66D of Information Technology Act."
        )
    )

    # 3. Generate report
    gen_resp = client.post(
        f"/api/documents/{doc.id}/generate-report/",
        data={"language": "en"},
        content_type="application/json",
        **headers
    )
    assert gen_resp.status_code == 200
    rep_data = gen_resp.json()
    assert rep_data["report_id"].startswith("LM-")
    assert rep_data["version"] == 1
    assert "complaint_type" in rep_data
    assert "legal_provisions" in rep_data
    report_id = rep_data["id"]

    # 4. Fetch latest report
    latest_resp = client.get(f"/api/documents/{doc.id}/reports/latest/", **headers)
    assert latest_resp.status_code == 200
    assert latest_resp.json()["id"] == report_id

    # 5. List reports
    list_resp = client.get(f"/api/documents/{doc.id}/reports/", **headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["count"] == 1

    # 6. Download PDF
    pdf_resp = client.get(f"/api/documents/{doc.id}/reports/{report_id}/pdf/", **headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp["Content-Type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF")
    assert len(pdf_resp.content) > 1000

    # 7. Regenerate creates version 2
    gen_resp_v2 = client.post(
        f"/api/documents/{doc.id}/generate-report/",
        data={"language": "en"},
        content_type="application/json",
        **headers
    )
    assert gen_resp_v2.status_code == 200
    assert gen_resp_v2.json()["version"] == 2

    # Check total reports count is 2
    list_resp_v2 = client.get(f"/api/documents/{doc.id}/reports/", **headers)
    assert list_resp_v2.json()["count"] == 2

