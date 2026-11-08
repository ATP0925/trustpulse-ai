"""
Test FastMCP Tools for TrustPulse AI
"""

import os
import sys
import json
from pathlib import Path
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from trustpulse_mcp import (
    onboard_business,
    get_business_analytics,
    generate_counter_table_tent,
    generate_whatsapp_review_invite,
    simulate_customer_review
)

def test_mcp_onboard_business():
    res_str = onboard_business(
        name="Apollo Dental Whitefield",
        category="Dental Clinic",
        google_review_url="https://maps.google.com/?cid=11223344",
        phone="+91 80 1234 5678",
        offer_text="Complimentary dental X-ray with cleaning!"
    )
    res = json.loads(res_str)
    assert res["status"] == "success"
    assert res["business_slug"] == "apollo-dental-whitefield"
    assert "review_filter_url" in res
    assert "printable_poster_pdf" in res

def test_mcp_simulate_review_routing():
    # Test 5-star rating -> Google Maps
    pos_str = simulate_customer_review(
        slug="apollo-dental-whitefield",
        rating=5,
        customer_name="Anita Roy"
    )
    pos = json.loads(pos_str)
    assert pos["action_taken"] == "REDIRECTED_TO_GOOGLE_MAPS"
    assert pos["redirected_to_google"] is True

    # Test 2-star rating -> Shielded into private inbox
    neg_str = simulate_customer_review(
        slug="apollo-dental-whitefield",
        rating=2,
        customer_name="Karan Malhotra",
        customer_phone="+91 99887 66554",
        feedback="Reception staff was rude and doctor arrived late."
    )
    neg = json.loads(neg_str)
    assert neg["action_taken"] == "SHIELDED_INTO_PRIVATE_INBOX"
    assert neg["redirected_to_google"] is False

def test_mcp_get_analytics():
    res_str = get_business_analytics("apollo-dental-whitefield")
    res = json.loads(res_str)
    assert res["business_name"] == "Apollo Dental Whitefield"
    assert res["metrics"]["google_redirects_5star"] >= 1
    assert res["metrics"]["negative_reviews_shielded"] >= 1

def test_mcp_whatsapp_invite():
    res_str = generate_whatsapp_review_invite(
        slug="apollo-dental-whitefield",
        customer_name="Vikram Singh",
        customer_phone="919876543210"
    )
    res = json.loads(res_str)
    assert res["status"] == "success"
    assert "wa.me/919876543210" in res["whatsapp_url"]
    assert "apollo-dental-whitefield" in res["message_text"]

def test_mcp_generate_table_tent():
    res_str = generate_counter_table_tent("apollo-dental-whitefield")
    res = json.loads(res_str)
    assert res["status"] == "success"
    assert res["file_size_bytes"] > 2000
