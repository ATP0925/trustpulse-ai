#!/usr/bin/env python3
"""
TrustPulse AI - Autonomous Hunter & Business Onboarding Daemon
Autonomously processes targeted business leads, provisions their review shields,
generates custom print-ready counter posters, and stages personalized outreach dispatches.
"""

import os
import sys
import json
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from trustpulse_mcp import onboard_business
from outreach.free_demo_onboarding import slugify

TARGET_PROSPECTS = [
    {
        "name": "Dr. Batra's Positive Health Clinic",
        "category": "Homeopathy & Trichology",
        "city": "Mumbai",
        "google_url": "https://maps.google.com/?cid=987123456",
        "phone": "+91 22 6666 8888",
        "owner_email": "customercare@drbatras.com",
        "offer_text": "Complimentary hair & scalp analysis voucher!"
    },
    {
        "name": "Gold's Gym Bandra West",
        "category": "Fitness & Wellness",
        "city": "Mumbai",
        "google_url": "https://maps.google.com/?cid=123987456",
        "phone": "+91 98201 99999",
        "owner_email": "bandra@goldsgym.in",
        "offer_text": "1 Free Personal Training Session + Protein Shake!"
    },
    {
        "name": "Enrich Salon & Luxury Spa",
        "category": "Hair & Beauty Salon",
        "city": "Pune",
        "google_url": "https://maps.google.com/?cid=456123789",
        "phone": "+91 20 2567 1111",
        "owner_email": "care@enrichsalon.com",
        "offer_text": "₹300 discount on haircut & styling!"
    },
    {
        "name": "Kalyan Jewellers Showroom",
        "category": "Luxury Retail",
        "city": "Bengaluru",
        "google_url": "https://maps.google.com/?cid=789456123",
        "phone": "+91 80 4123 4567",
        "owner_email": "customercare@kalyanjewellers.net",
        "offer_text": "Exclusive silver coin voucher with your purchase!"
    },
    {
        "name": "Dr. Lal PathLabs Collection Center",
        "category": "Diagnostic & Pathology",
        "city": "New Delhi",
        "google_url": "https://maps.google.com/?cid=321654987",
        "phone": "+91 11 3988 5050",
        "owner_email": "support@lalpathlabs.com",
        "offer_text": "10% discount on complete health checkup package!"
    }
]

def run_autonomous_hunter(domain: str = "http://localhost:8000"):
    print("=" * 70)
    print("⚡ TRUSTPULSE AUTONOMOUS HUNTER DAEMON INITIALIZING...")
    print(f"Targeting {len(TARGET_PROSPECTS)} high-value local business prospects.")
    print("=" * 70)

    ledger_path = APP_DIR / "data" / "outreach_dispatch_ledger.json"
    results = []

    for prospect in TARGET_PROSPECTS:
        name = prospect["name"]
        print(f"\n[Processing] -> {name} ({prospect['city']} | {prospect['category']})")
        
        # Call FastMCP Tool
        res_str = onboard_business(
            name=name,
            category=prospect["category"],
            google_review_url=prospect["google_url"],
            phone=prospect["phone"],
            owner_email=prospect["owner_email"],
            offer_text=prospect["offer_text"]
        )
        res = json.loads(res_str)
        slug = res["business_slug"]

        # Craft personalized high-converting pitch
        pitch_msg = (
            f"Hello {name} Team! 👋\n\n"
            f"We noticed your location in {prospect['city']} on Google Maps. "
            f"In {prospect['city']}, 85% of high-intent customers choose businesses with 4.8★+ ratings over competitors.\n\n"
            f"We have provisioned a custom Reputation Accelerator & Negative Review Shield for {name}:\n"
            f"🔗 Live Interactive Review Filter: {domain}/r/{slug}\n"
            f"📊 Private Manager Analytics Dashboard: {domain}/dashboard/{slug}\n"
            f"🖨️ Ready-to-Print Counter Table-Tent PDF: {domain}/poster/{slug}\n\n"
            f"How TrustPulse protects your {prospect['category']}:\n"
            f"• Happy customers (4-5 stars) are routed in 1-tap directly to your Google Maps review page.\n"
            f"• Unhappy customers (1-3 stars) are privately intercepted into your manager dashboard so bad reviews NEVER appear on Google!\n\n"
            f"We have activated a 14-day free trial on your account. Zero setup required.\n"
            f"Reply to this message or WhatsApp us to keep it active for ₹999/month.\n"
        )

        pitch_file = APP_DIR / "data" / f"pitch_{slug}.txt"
        pitch_file.write_text(pitch_msg, encoding="utf-8")

        item = {
            "business_name": name,
            "category": prospect["category"],
            "city": prospect["city"],
            "slug": slug,
            "review_url": f"{domain}/r/{slug}",
            "dashboard_url": f"{domain}/dashboard/{slug}",
            "poster_pdf": res["printable_poster_pdf"],
            "pitch_file": str(pitch_file),
            "phone": prospect["phone"],
            "email": prospect["owner_email"],
            "status": "PROVISIONED_AND_READY_FOR_DISPATCH"
        }
        results.append(item)
        print(f"  ✓ Provisioned Review Shield: {domain}/r/{slug}")
        print(f"  ✓ Generated Printable PDF: {res['printable_poster_pdf']}")
        print(f"  ✓ Saved Personalized Pitch: {pitch_file.name}")

    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print(f"🎉 COMPLETED: {len(results)} Businesses Fully Onboarded with Live Demos & Posters!")
    print(f"Ledger saved to: {ledger_path}")
    print("=" * 70)

if __name__ == "__main__":
    run_autonomous_hunter()

