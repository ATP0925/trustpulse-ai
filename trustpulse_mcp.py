"""
TrustPulse AI - Official FastMCP Server
Exposes Model Context Protocol (MCP) tools for AI agents to autonomously
onboard businesses, generate printable table tents, monitor review analytics,
and dispatch review invites.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path
from mcp.server.fastmcp import FastMCP

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from core.database import (
    init_db,
    create_or_update_business,
    get_business_by_slug,
    get_analytics,
    log_review,
    log_scan
)
from core.qr_poster_gen import generate_table_tent_pdf
from outreach.free_demo_onboarding import slugify

# Initialize FastMCP Server
mcp = FastMCP("TrustPulse-Reputation-Engine")

@mcp.tool()
def onboard_business(
    name: str,
    category: str,
    google_review_url: str,
    phone: str = "",
    owner_email: str = "",
    offer_text: str = "Scan to rate us & receive ₹200 off your next appointment!"
) -> str:
    """
    Onboard a local business to TrustPulse AI.
    Generates their custom review filter URL, dashboard URL, and printable PDF table tent.
    """
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

    review_url = f"http://localhost:8000/r/{slug}"
    dashboard_url = f"http://localhost:8000/dashboard/{slug}"
    pdf_out = APP_DIR / "data" / f"poster_{slug}.pdf"

    generate_table_tent_pdf(
        business_name=name,
        review_url=review_url,
        offer_text=offer_text,
        output_pdf=str(pdf_out)
    )

    return json.dumps({
        "status": "success",
        "business_id": bid,
        "business_slug": slug,
        "business_name": name,
        "review_filter_url": review_url,
        "manager_dashboard_url": dashboard_url,
        "printable_poster_pdf": str(pdf_out)
    }, indent=2)

@mcp.tool()
def get_business_analytics(slug: str) -> str:
    """
    Retrieve real-time reputation metrics for a business by its slug.
    Returns total scans, 5-star Google redirects, negative reviews shielded, and complaints.
    """
    init_db()
    biz = get_business_by_slug(slug)
    if not biz:
        return json.dumps({"status": "error", "message": f"Business '{slug}' not found."})
    
    analytics = get_analytics(biz["id"])
    return json.dumps({
        "business_name": biz["name"],
        "category": biz["category"],
        "metrics": analytics
    }, indent=2)

@mcp.tool()
def generate_counter_table_tent(slug: str) -> str:
    """
    Generates a high-resolution printable PDF Table-Tent counter poster for a registered business.
    """
    init_db()
    biz = get_business_by_slug(slug)
    if not biz:
        return json.dumps({"status": "error", "message": f"Business '{slug}' not found."})

    pdf_out = APP_DIR / "data" / f"poster_{slug}.pdf"
    generate_table_tent_pdf(
        business_name=biz["name"],
        review_url=f"http://localhost:8000/r/{slug}",
        offer_text=biz["offer_text"],
        output_pdf=str(pdf_out)
    )

    return json.dumps({
        "status": "success",
        "poster_path": str(pdf_out),
        "file_size_bytes": os.path.getsize(pdf_out)
    }, indent=2)

@mcp.tool()
def generate_whatsapp_review_invite(slug: str, customer_name: str, customer_phone: str) -> str:
    """
    Generates a personalized 1-click WhatsApp review invitation link with direct perk incentive.
    """
    init_db()
    biz = get_business_by_slug(slug)
    if not biz:
        return json.dumps({"status": "error", "message": f"Business '{slug}' not found."})

    review_link = f"http://localhost:8000/r/{slug}"
    message = (
        f"Hello {customer_name}! 👋 Thank you for visiting {biz['name']} today. "
        f"How was your experience? Tap here to rate us and unlock {biz['offer_text']}: {review_link}"
    )
    encoded = urllib.parse.quote(message)
    wa_url = f"https://wa.me/{customer_phone}?text={encoded}"

    return json.dumps({
        "status": "success",
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "whatsapp_url": wa_url,
        "message_text": message
    }, indent=2)

@mcp.tool()
def simulate_customer_review(
    slug: str,
    rating: int,
    customer_name: str = "",
    customer_phone: str = "",
    feedback: str = ""
) -> str:
    """
    Simulates a customer review submission through the Smart Review Filter.
    Ratings 4-5 are routed to Google Maps; ratings 1-3 are shielded into private management feedback.
    """
    init_db()
    biz = get_business_by_slug(slug)
    if not biz:
        return json.dumps({"status": "error", "message": f"Business '{slug}' not found."})

    min_stars = biz.get("min_stars_for_google", 4)
    redirected = (rating >= min_stars)

    rev_id = log_review(
        business_id=biz["id"],
        rating=rating,
        redirected=redirected,
        customer_name=customer_name,
        customer_phone=customer_phone,
        feedback=feedback
    )

    return json.dumps({
        "status": "success",
        "review_id": rev_id,
        "rating": rating,
        "redirected_to_google": redirected,
        "action_taken": "REDIRECTED_TO_GOOGLE_MAPS" if redirected else "SHIELDED_INTO_PRIVATE_INBOX"
    }, indent=2)

if __name__ == "__main__":
    # Run the FastMCP server on stdio
    mcp.run()

