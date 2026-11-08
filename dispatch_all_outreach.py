#!/usr/bin/env python3
"""
TrustPulse AI - Batch Outreach Dispatcher
Reads the onboarded prospect ledger, stages or sends emails with attached PDF posters,
and prepares 1-click WhatsApp triggers.
"""

import os
import sys
import json
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from outreach.communications_gateway import CommunicationsGateway

def dispatch_all():
    ledger_path = APP_DIR / "data" / "outreach_dispatch_ledger.json"
    if not ledger_path.exists():
        print("No outreach ledger found. Run autonomous_hunter.py first.")
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        prospects = json.load(f)

    gateway = CommunicationsGateway()
    print(f"🚀 Dispatching outreach packages for {len(prospects)} businesses...\n")

    for p in prospects:
        name = p["business_name"]
        email = p["email"]
        category = p["category"]
        review_url = p["review_url"]
        dashboard_url = p["dashboard_url"]
        poster_pdf = p["poster_pdf"]

        print(f"[{name}]")
        # Dispatch or stage email
        gateway.send_email_with_pdf(
            to_email=email,
            business_name=name,
            category=category,
            review_url=review_url,
            dashboard_url=dashboard_url,
            pdf_attachment_path=poster_pdf
        )

    print("\n✅ All 5 client packages have been staged / dispatched!")

if __name__ == "__main__":
    dispatch_all()

