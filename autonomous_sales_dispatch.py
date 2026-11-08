#!/usr/bin/env python3
"""
TrustPulse AI - Autonomous Sales & Outreach Dispatch Manager
Prepares 1-click WhatsApp outreach triggers, live review URLs, and printable counter PDFs
for all 17 onboarded business prospects.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PRODUCTION_DOMAIN = "https://atp0925.github.io/trustpulse-ai"

def generate_sales_ledger():
    biz_json_path = APP_DIR / "businesses.json"
    if not biz_json_path.exists():
        print("businesses.json not found.")
        return

    with open(biz_json_path, "r", encoding="utf-8") as f:
        businesses = json.load(f)

    sales_pack = []

    for biz in businesses:
        name = biz["name"]
        cat = biz["category"]
        slug = biz["slug"]
        phone = biz["phone"] or "+91 98200 12345"
        clean_phone = "".join(filter(str.isdigit, phone))
        offer = biz["offer_text"]

        live_review_url = f"{PRODUCTION_DOMAIN}/r/{slug}/index.html"
        dashboard_url = f"{PRODUCTION_DOMAIN}/dashboard/{slug}/index.html"
        poster_pdf_url = f"{PRODUCTION_DOMAIN}/posters/poster_{slug}.pdf"

        # High-converting WhatsApp pitch
        pitch_msg = (
            f"Hello {name} Team! 👋\n\n"
            f"Did you know that 87% of local patients check your Google Maps rating before visiting your {cat} practice?\n\n"
            f"We have set up an automated 5-Star Review Shield for your location:\n"
            f"⭐ Happy Patients (4-5★) -> Automatically post on Google Maps in 5 seconds.\n"
            f"🛡️ Unhappy Patients (1-3★) -> Intercepted privately to your management so zero bad reviews hit Google!\n\n"
            f"📱 Test Your Clinic's Live Filter: {live_review_url}\n"
            f"📊 View Your Live Dashboard: {dashboard_url}\n"
            f"🖨️ Download Your Print-Ready Counter Stand: {poster_pdf_url}\n\n"
            f"Activate for your location for just ₹999/month (Risk-free 14-day trial)."
        )

        encoded_pitch = urllib.parse.quote(pitch_msg)
        wa_desktop_uri = f"whatsapp://send?phone={clean_phone}&text={encoded_pitch}"
        wa_web_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_pitch}"

        lead = {
            "name": name,
            "category": cat,
            "slug": slug,
            "phone": phone,
            "live_review_url": live_review_url,
            "dashboard_url": dashboard_url,
            "poster_pdf_url": poster_pdf_url,
            "pitch_message": pitch_msg,
            "wa_desktop_uri": wa_desktop_uri,
            "wa_web_url": wa_web_url,
            "status": "READY_FOR_ENGAGEMENT"
        }
        sales_pack.append(lead)

    out_path = APP_DIR / "data" / "active_sales_prospects.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sales_pack, f, indent=2)

    print(f"✅ Generated sales pack for {len(sales_pack)} businesses at: {out_path}")
    return sales_pack

if __name__ == "__main__":
    generate_sales_ledger()
