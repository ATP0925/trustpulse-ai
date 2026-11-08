#!/usr/bin/env python3
"""
TrustPulse AI - 1-Click Client Onboarding & Demo Generator
Creates a custom business account, generates their live review filter link,
prints their branded counter table-tent PDF, and writes a personalized WhatsApp pitch.
"""

import os
import sys
import argparse
import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from core.database import init_db, create_or_update_business
from core.qr_poster_gen import generate_table_tent_pdf

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

def onboard_client(
    name: str,
    category: str,
    google_review_url: str,
    phone: str = "",
    owner_email: str = "",
    offer_text: str = "Scan to rate us & unlock ₹200 off your next appointment!",
    domain: str = "http://localhost:8000"
):
    init_db()
    slug = slugify(name)
    bid = create_or_update_business(
        slug=slug,
        name=name,
        category=category,
        google_review_url=google_review_url,
        phone=phone,
        owner_email=owner_email,
        min_stars=4,
        offer_text=offer_text
    )

    review_url = f"{domain}/r/{slug}"
    dashboard_url = f"{domain}/dashboard/{slug}"
    pdf_out = APP_DIR / "data" / f"poster_{slug}.pdf"

    generate_table_tent_pdf(
        business_name=name,
        review_url=review_url,
        offer_text=offer_text,
        output_pdf=str(pdf_out)
    )

    # WhatsApp Pitch Text
    wa_pitch = f"""
Hello {name}! 👋

I noticed your clinic on Google Maps. You have great patient care, but in our local area, Google Maps ranking directly controls how many new walk-in patients choose your clinic over competitors.

I built a custom Reputation Accelerator & Negative Review Shield for {name}:
🔗 Live Interactive Demo: {review_url}

How it protects your clinic:
1. Happy patients (4-5 stars) are routed in 1-tap directly to Google Maps.
2. Unhappy patients (1-3 stars) are intercepted into a private manager inbox so bad reviews NEVER appear publicly on Google!
3. Includes a print-ready counter card for your reception desk (Attached PDF).

I would love to set this up for you completely free for 14 days. If it brings you even 5 new 5-star reviews, subscription is just ₹999/month.

Let me know if you'd like me to activate your manager dashboard!
"""

    print("=" * 65)
    print(f"🎉 CLIENT ONBOARDED: {name} (ID: {bid})")
    print(f"🔗 Customer Review URL:   {review_url}")
    print(f"📊 Manager Dashboard:     {dashboard_url}")
    print(f"🖨️ Counter Table-Tent PDF: {pdf_out}")
    print("=" * 65)
    print("📋 READY-TO-SEND WHATSAPP PITCH:")
    print(wa_pitch)
    print("=" * 65)

    # Save pitch to text file
    pitch_file = APP_DIR / "data" / f"pitch_{slug}.txt"
    pitch_file.write_text(wa_pitch, encoding="utf-8")
    print(f"Pitch saved to: {pitch_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard new business to TrustPulse")
    parser.add_argument("--name", default="Dr. Joshi Orthopedic & Spine Clinic", help="Business Name")
    parser.add_argument("--category", default="Orthopedic & Spine Clinic", help="Category")
    parser.add_argument("--google", default="https://maps.google.com/?cid=123456789", help="Google Review URL")
    parser.add_argument("--phone", default="+91 98900 12345", help="Phone")
    parser.add_argument("--offer", default="Scan to rate us & receive priority appointment booking!", help="Customer Perk Offer")
    args = parser.parse_args()

    onboard_client(
        name=args.name,
        category=args.category,
        google_review_url=args.google,
        phone=args.phone,
        offer_text=args.offer
    )

