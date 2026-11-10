# TrustPulse AI

> Local business reputation gatekeeper and smart review routing engine.

TrustPulse AI helps local businesses, clinics, and restaurants protect their online rating. It provides a simple QR-based checkout flow: satisfied customers (4-5 stars) are directed straight to Google Maps to leave a public review, while critical feedback (1-3 stars) is captured privately in an owner dashboard before it turns into a negative public rating.

---

## The Problem It Solves

Most happy customers leave without posting a review. Unhappy customers, however, are 3x more likely to voice frustration publicly on Google Maps or Yelp.

TrustPulse balances this dynamic:
1. **At checkout / table:** The customer scans a branded counter QR code.
2. **Dynamic Review Gate:** The customer picks a 1-5 star rating on a lightweight mobile web page.
3. **Smart Routing:**
   - **4–5 Stars:** Instantly redirected to the business's verified Google Maps review box with pre-filled 5-star intent.
   - **1–3 Stars:** Opens a private feedback form. The complaint is logged into SQLite and the owner receives immediate notification to resolve the issue privately.
4. **Automated Printable Merch:** Generates ready-to-print PDF table tents and counter cards with customized QR codes on demand.

---

## System Architecture

```text
               Customer Scans Table-Tent QR
                           │
                           ▼
               Lightweight Mobile Web Interface (/r/{slug})
                           │
                 [Customer Star Rating]
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
       4 or 5 Stars                  1 to 3 Stars
            │                             │
    Instant Redirect              Private Feedback Form
            │                             │
    Google Maps Reviews            Saved to SQLite DB
                                  + Owner Alert Dispatched
```

---

## Key Features

- **Zero-Friction Mobile Web Client:** No app download required. Fast loading (<1s) even on flaky cellular data.
- **Dynamic PDF Generator:** Built-in PDF table-tent generator creates print-ready A5/counter card designs with high-res QR codes.
- **Owner Analytics Dashboard:** Tracks daily scan counts, conversion rates (scan-to-review ratio), and private complaints in real time.
- **FastAPI + SQLite Core:** Self-contained, lightweight backend with zero bloated external services.

---

## Getting Started

### 1. Requirements
- Python 3.10+
- Virtual environment (recommended)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/ATP0925/trustpulse-ai.git
cd trustpulse-ai

# Install dependencies
pip install fastapi uvicorn pydantic jinja2 reportlab qrcode
```

### 3. Run the Server
```bash
python server.py
```
The server will boot locally at `http://localhost:8000`.

- **Review Flow (Mobile Demo):** `http://localhost:8000/r/dr-smile-dental`
- **Owner Dashboard:** `http://localhost:8000/dashboard/dr-smile-dental`
- **Download Printable Table-Tent PDF:** `http://localhost:8000/poster/dr-smile-dental`

---

## Tech Stack

- **Backend:** FastAPI, Python, Pydantic
- **Database:** SQLite
- **Templating & UI:** Jinja2, Mobile-First Vanilla CSS/JS
- **Document Generation:** ReportLab, `qrcode`

---

## License

MIT License. Built by [ATP0925](https://github.com/ATP0925).
