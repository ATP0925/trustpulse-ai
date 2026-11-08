"""
TrustPulse AI - SQLite Storage & Analytics Database
Manages business accounts, Google Maps redirect configurations,
scanned review events, and negative review isolation logs.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "trustpulse.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Businesses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        phone TEXT,
        owner_email TEXT,
        owner_whatsapp TEXT,
        google_review_url TEXT NOT NULL,
        min_stars_for_google INTEGER DEFAULT 4,
        offer_text TEXT DEFAULT '10% discount on your next visit',
        subscription_status TEXT DEFAULT 'ACTIVE',
        subscription_tier TEXT DEFAULT 'STARTER',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Reviews and feedback log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        redirected_to_google BOOLEAN NOT NULL,
        customer_name TEXT,
        customer_phone TEXT,
        private_feedback TEXT,
        resolved BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (business_id) REFERENCES businesses (id)
    )
    """)

    # Analytics scans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        user_agent TEXT,
        ip_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (business_id) REFERENCES businesses (id)
    )
    """)

    conn.commit()
    conn.close()

def create_or_update_business(
    slug: str,
    name: str,
    category: str,
    google_review_url: str,
    phone: str = "",
    owner_email: str = "",
    owner_whatsapp: str = "",
    min_stars: int = 4,
    offer_text: str = "10% off on your next visit"
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO businesses (slug, name, category, google_review_url, phone, owner_email, owner_whatsapp, min_stars_for_google, offer_text)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(slug) DO UPDATE SET
        name=excluded.name,
        category=excluded.category,
        google_review_url=excluded.google_review_url,
        phone=excluded.phone,
        owner_email=excluded.owner_email,
        owner_whatsapp=excluded.owner_whatsapp,
        min_stars_for_google=excluded.min_stars_for_google,
        offer_text=excluded.offer_text
    """, (slug, name, category, google_review_url, phone, owner_email, owner_whatsapp, min_stars, offer_text))
    conn.commit()
    biz_id = cursor.lastrowid
    conn.close()
    return biz_id

def get_business_by_slug(slug: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM businesses WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def log_scan(business_id: int, user_agent: str = "", ip_hash: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO qr_scans (business_id, user_agent, ip_hash) VALUES (?, ?, ?)", (business_id, user_agent, ip_hash))
    conn.commit()
    conn.close()

def log_review(business_id: int, rating: int, redirected: bool, customer_name: str = "", customer_phone: str = "", feedback: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reviews_log (business_id, rating, redirected_to_google, customer_name, customer_phone, private_feedback)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (business_id, rating, redirected, customer_name, customer_phone, feedback))
    conn.commit()
    rev_id = cursor.lastrowid
    conn.close()
    return rev_id

def get_analytics(business_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM qr_scans WHERE business_id = ?", (business_id,))
    total_scans = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM reviews_log WHERE business_id = ? AND redirected_to_google = 1", (business_id,))
    google_redirects = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM reviews_log WHERE business_id = ? AND redirected_to_google = 0", (business_id,))
    negative_shields = cursor.fetchone()['count']

    cursor.execute("SELECT AVG(rating) as avg_rating FROM reviews_log WHERE business_id = ?", (business_id,))
    avg_row = cursor.fetchone()
    avg_rating = round(avg_row['avg_rating'], 1) if avg_row and avg_row['avg_rating'] else 5.0

    cursor.execute("SELECT * FROM reviews_log WHERE business_id = ? ORDER BY created_at DESC LIMIT 15", (business_id,))
    recent_reviews = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_scans": total_scans,
        "google_redirects_5star": google_redirects,
        "negative_reviews_shielded": negative_shields,
        "internal_avg_rating": avg_rating,
        "recent_reviews": recent_reviews
    }

if __name__ == "__main__":
    init_db()
    # Create sample demo business
    bid = create_or_update_business(
        slug="dr-smile-dental",
        name="Dr. Smile Dental & Laser Clinic",
        category="Dental Clinic",
        google_review_url="https://maps.google.com/?cid=1029384756",
        phone="+91 98200 12345",
        owner_email="dr.smile@clinic.com",
        owner_whatsapp="+919820012345",
        min_stars=4,
        offer_text="Get ₹200 off your next cleaning session!"
    )
    print(f"✅ Initialized TrustPulse database & demo business with ID: {bid}")

