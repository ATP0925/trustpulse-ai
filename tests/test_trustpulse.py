"""
Unit & Integration Test Suite for TrustPulse AI
Verifies database persistence, QR generation, PDF table-tent rendering,
smart review routing (4-5 star redirect vs 1-3 star shield), and FastAPI endpoints.
"""

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from core.database import (
    init_db,
    create_or_update_business,
    get_business_by_slug,
    log_scan,
    log_review,
    get_analytics
)
from core.qr_poster_gen import generate_qr_image, generate_table_tent_pdf
from server import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()

def test_01_create_and_fetch_business():
    biz_id = create_or_update_business(
        slug="test-dental-hub",
        name="Apex Dental Care",
        category="Dental Clinic",
        google_review_url="https://maps.google.com/?cid=999888777",
        phone="+91 98000 11111",
        owner_email="apex@dental.in",
        min_stars=4,
        offer_text="Get 15% off dental cleanings!"
    )
    assert biz_id is not None
    biz = get_business_by_slug("test-dental-hub")
    assert biz["name"] == "Apex Dental Care"
    assert biz["category"] == "Dental Clinic"
    assert biz["min_stars_for_google"] == 4

def test_02_qr_scan_logging_and_analytics():
    biz = get_business_by_slug("test-dental-hub")
    log_scan(biz["id"], user_agent="Mozilla/5.0 iPhone")
    log_scan(biz["id"], user_agent="Mozilla/5.0 Android")
    
    analytics = get_analytics(biz["id"])
    assert analytics["total_scans"] >= 2

def test_03_positive_review_routing():
    biz = get_business_by_slug("test-dental-hub")
    # Customer gives 5 stars -> Redirects to Google
    rev_id = log_review(biz["id"], rating=5, redirected=True)
    assert rev_id is not None

    analytics = get_analytics(biz["id"])
    assert analytics["google_redirects_5star"] >= 1

def test_04_negative_review_shielding():
    biz = get_business_by_slug("test-dental-hub")
    # Customer gives 2 stars -> Shielded from Google, private complaint captured
    rev_id = log_review(
        business_id=biz["id"],
        rating=2,
        redirected=False,
        customer_name="Pooja Verma",
        customer_phone="+91 98111 22222",
        feedback="Waiting time was 45 minutes past my appointment schedule."
    )
    assert rev_id is not None

    analytics = get_analytics(biz["id"])
    assert analytics["negative_reviews_shielded"] >= 1
    # Check that feedback is recorded
    recent = analytics["recent_reviews"]
    matched = [r for r in recent if r["customer_name"] == "Pooja Verma"]
    assert len(matched) > 0
    assert matched[0]["private_feedback"] == "Waiting time was 45 minutes past my appointment schedule."

def test_05_qr_code_generation(tmp_path):
    qr_out = tmp_path / "test_qr.png"
    res = generate_qr_image("http://localhost:8000/r/test-dental-hub", str(qr_out))
    assert os.path.exists(res)
    assert os.path.getsize(res) > 500

def test_06_table_tent_pdf_generation(tmp_path):
    pdf_out = tmp_path / "test_counter_poster.pdf"
    res = generate_table_tent_pdf(
        business_name="Apex Dental Care",
        review_url="http://localhost:8000/r/test-dental-hub",
        offer_text="Scan to win a discount & review us on Google",
        output_pdf=str(pdf_out)
    )
    assert os.path.exists(res)
    assert os.path.getsize(res) > 2000

def test_07_fastapi_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "TrustPulse" in response.text
    assert "₹999" in response.text

def test_08_fastapi_review_filter_endpoint():
    response = client.get("/r/test-dental-hub")
    assert response.status_code == 200
    assert "Apex Dental Care" in response.text
    assert "starContainer" in response.text

def test_09_fastapi_dashboard_endpoint():
    response = client.get("/dashboard/test-dental-hub")
    assert response.status_code == 200
    assert "Reputation Command Center" in response.text
    assert "Total QR Scans" in response.text

def test_10_fastapi_api_log_review():
    biz = get_business_by_slug("test-dental-hub")
    payload = {
        "business_id": biz["id"],
        "rating": 5,
        "redirected": True
    }
    response = client.post("/api/log-review", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_11_fastapi_api_feedback():
    biz = get_business_by_slug("test-dental-hub")
    payload = {
        "business_id": biz["id"],
        "rating": 1,
        "customer_name": "Rohan Mehra",
        "customer_phone": "+91 98333 44444",
        "feedback": "Dr was in a rush, unhelpful explanation."
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["review_id"] > 0

