#!/usr/bin/env python3
"""
TrustPulse AI - Autonomous Communications & Outreach Gateway
Dispatches personalized client pitches, demo links, and printable table-tent posters
via WhatsApp desktop protocol and multi-provider transactional email.
"""

import os
import sys
import json
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
import subprocess

APP_DIR = Path(__file__).resolve().parent.parent

class CommunicationsGateway:
    def __init__(self, smtp_host=None, smtp_port=587, smtp_user=None, smtp_pass=None):
        self.smtp_host = smtp_host or os.getenv("TRUSTPULSE_SMTP_HOST")
        self.smtp_port = int(smtp_port or os.getenv("TRUSTPULSE_SMTP_PORT", 587))
        self.smtp_user = smtp_user or os.getenv("TRUSTPULSE_SMTP_USER")
        self.smtp_pass = smtp_pass or os.getenv("TRUSTPULSE_SMTP_PASS")

    def trigger_whatsapp_desktop(self, phone: str, message: str) -> bool:
        """
        Triggers Windows WhatsApp client to open chat with pre-filled message.
        """
        # Clean phone number (strip spaces, +, dashes)
        clean_phone = "".join(filter(str.isdigit, phone))
        encoded_msg = urllib.parse.quote(message)
        uri = f"whatsapp://send?phone={clean_phone}&text={encoded_msg}"

        try:
            print(f"Opening WhatsApp desktop chat for: +{clean_phone}...")
            # On Windows, start URI via explorer/powershell
            subprocess.run(["cmd", "/c", "start", "", uri], check=True, shell=True)
            print("✓ WhatsApp client brought to foreground with pre-filled pitch.")
            return True
        except Exception as e:
            print(f"Failed to launch WhatsApp URI: {e}")
            return False

    def build_html_email(self, business_name: str, category: str, review_url: str, dashboard_url: str) -> str:
        """
        Constructs high-converting HTML outreach email.
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
                .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
                .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; background: #dbeafe; color: #1d4ed8; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 16px; }}
                h1 {{ font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 0; }}
                p {{ font-size: 14px; line-height: 1.6; color: #475569; }}
                .btn {{ display: inline-block; padding: 12px 24px; border-radius: 10px; background: #2563eb; color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; margin-top: 12px; }}
                .feature-box {{ background: #f1f5f9; border-radius: 12px; padding: 16px; margin: 20px 0; font-size: 13px; }}
                .footer {{ text-align: center; margin-top: 24px; font-size: 11px; color: #94a3b8; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">Google Reputation Protection</div>
                <h1>A Custom 5-Star Review Shield for {business_name}</h1>
                <p>Hello Management Team,</p>
                <p>In your area, Google Maps rating directly determines which {category} patients and customers choose first. Just a few unaddressed 1-star reviews can quietly cost your practice lakhs in missed walk-ins.</p>
                
                <div class="feature-box">
                    <b>How TrustPulse AI Protects {business_name}:</b><br/>
                    • <b>Happy Patients (4-5★):</b> Routed in 1-tap directly to post their official Google Maps review.<br/>
                    • <b>Unhappy Patients (1-3★):</b> Intercepted privately into your manager inbox so negative complaints NEVER appear on Google!<br/>
                    • <b>Print-Ready Counter QR Stand:</b> Place it at your reception desk or billing counter.
                </div>

                <p>We have pre-configured a live 14-day trial for your location:</p>
                <a href="{review_url}" class="btn">Test Your Live Review Filter →</a>

                <p style="margin-top: 24px; font-size: 12px; color: #64748b;">
                    Attached is your clinic's branded A5 counter table-tent PDF. You can print it today.<br/>
                    Subscription to keep it active is just ₹999/month.
                </p>
                
                <div class="footer">
                    Sent autonomously by TrustPulse AI Technologies • Reputation Automation
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def send_email_with_pdf(
        self,
        to_email: str,
        business_name: str,
        category: str,
        review_url: str,
        dashboard_url: str,
        pdf_attachment_path: str = None
    ) -> bool:
        """
        Sends HTML email with optional attached PDF counter tent poster.
        """
        if not self.smtp_host or not self.smtp_user:
            print(f"⚠️ SMTP credentials not set. Staging email dispatch locally for {to_email}...")
            # Save draft to disk
            draft_path = APP_DIR / "data" / f"email_draft_{slugify(business_name)}.html"
            html_content = self.build_html_email(business_name, category, review_url, dashboard_url)
            draft_path.write_text(html_content, encoding="utf-8")
            print(f"✓ Staged HTML email draft to: {draft_path.name}")
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = f"TrustPulse AI <{self.smtp_user}>"
            msg['To'] = to_email
            msg['Subject'] = f"Reputation Shield & Google Review Filter for {business_name}"

            html_body = self.build_html_email(business_name, category, review_url, dashboard_url)
            msg.attach(MIMEText(html_body, 'html'))

            if pdf_attachment_path and os.path.exists(pdf_attachment_path):
                with open(pdf_attachment_path, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_attachment_path))
                    msg.attach(attach)

            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"✅ Successfully dispatched live email to: {to_email}")
            return True
        except Exception as e:
            print(f"Failed to dispatch live email: {e}")
            return False

def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

if __name__ == "__main__":
    gateway = CommunicationsGateway()
    print("Testing Communications Gateway...")
    # Test HTML email builder and local staging
    gateway.send_email_with_pdf(
        to_email="customercare@drbatras.com",
        business_name="Dr. Batra's Positive Health Clinic",
        category="Homeopathy & Trichology",
        review_url="http://localhost:8000/r/dr-batras-positive-health-clinic",
        dashboard_url="http://localhost:8000/dashboard/dr-batras-positive-health-clinic",
        pdf_attachment_path=str(APP_DIR / "data" / "poster_dr-batras-positive-health-clinic.pdf")
    )

