#!/usr/bin/env python3
"""
TrustPulse AI - Web Application & Reputation Engine Server
Runs on FastAPI + Uvicorn with SQLite persistence, dynamic QR generation,
smart Google review routing, and PDF table-tent delivery.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from core.database import (
    init_db,
    get_business_by_slug,
    create_or_update_business,
    log_scan,
    log_review,
    get_analytics
)
from core.qr_poster_gen import generate_table_tent_pdf, generate_qr_image

app = FastAPI(title="TrustPulse AI", version="1.0.0")

# Setup templates and static
templates = Jinja2Templates(directory=str(APP_DIR / "public"))
app.mount("/static", StaticFiles(directory=str(APP_DIR / "public")), name="static")

# Request Models
class ReviewLogRequest(BaseModel):
    business_id: int
    rating: int
    redirected: bool

class FeedbackRequest(BaseModel):
    business_id: int
    rating: int
    customer_name: str
    customer_phone: str
    feedback: str

@app.on_event("startup")
def startup():
    init_db()
    # Seed default clinic if not present
    if not get_business_by_slug("dr-smile-dental"):
        create_or_update_business(
            slug="dr-smile-dental",
            name="Dr. Smile Dental & Laser Clinic",
            category="Cosmetic & Advanced Dentistry",
            google_review_url="https://maps.google.com/?cid=1029384756",
            phone="+91 98200 12345",
            owner_email="dr.smile@clinic.com",
            owner_whatsapp="+919820012345",
            min_stars=4,
            offer_text="Get ₹200 off your next appointment!"
        )

# 1. Commercial Landing Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    landing_path = APP_DIR / "public" / "landing.html"
    return HTMLResponse(content=landing_path.read_text(encoding="utf-8"))

# 2. Consumer Review Filter Page (Scanned via QR)
@app.get("/r/{slug}", response_class=HTMLResponse)
async def review_filter(request: Request, slug: str):
    biz = get_business_by_slug(slug)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Log the QR scan
    user_agent = request.headers.get("user-agent", "Unknown")
    log_scan(biz["id"], user_agent=user_agent)

    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"business": biz}
    )

# 3. Business Owner Dashboard
@app.get("/dashboard/{slug}", response_class=HTMLResponse)
async def dashboard(request: Request, slug: str):
    biz = get_business_by_slug(slug)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    
    stats = get_analytics(biz["id"])
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"business": biz, "stats": stats}
    )

# 4. Printable Table-Tent Counter PDF Generator
@app.get("/poster/{slug}")
async def download_poster(request: Request, slug: str):
    biz = get_business_by_slug(slug)
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    host = request.headers.get("host", "localhost:8000")
    proto = request.headers.get("x-forwarded-proto", "http")
    review_url = f"{proto}://{host}/r/{slug}"

    pdf_path = APP_DIR / "data" / f"poster_{slug}.pdf"
    generate_table_tent_pdf(
        business_name=biz["name"],
        review_url=review_url,
        offer_text=f"Scan to rate us & unlock {biz['offer_text']}!",
        output_pdf=str(pdf_path)
    )

    return FileResponse(
        path=str(pdf_path),
        filename=f"Counter_Table_Tent_{slug}.pdf",
        media_type="application/pdf"
    )

# 5. API: Log review event
@app.post("/api/log-review")
async def api_log_review(payload: ReviewLogRequest):
    log_review(
        business_id=payload.business_id,
        rating=payload.rating,
        redirected=payload.redirected
    )
    return {"status": "success"}

# 6. API: Submit 1-3 Star Private Feedback
@app.post("/api/feedback")
async def api_feedback(payload: FeedbackRequest):
    rev_id = log_review(
        business_id=payload.business_id,
        rating=payload.rating,
        redirected=False,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        feedback=payload.feedback
    )
    return {"status": "success", "review_id": rev_id}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting TrustPulse AI Server on http://localhost:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

