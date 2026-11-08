import os
import urllib.request
import json

api_key = os.getenv("RESEND_API_KEY", "re_placeholder")
url = "https://api.resend.com/emails"

payload = {
    "from": "onboarding@resend.dev",
    "to": ["atpadkarmaruti@gmail.com"],
    "subject": "🚀 TrustPulse AI Live Email Dispatch Test",
    "html": """
    <div style="font-family: sans-serif; padding: 20px; background: #0f172a; color: #ffffff; border-radius: 12px;">
        <h1 style="color: #38bdf8;">⚡ TrustPulse AI is LIVE!</h1>
        <p>Boss, the automated email engine is successfully connected and functioning!</p>
        <p>Autonomous communications gateway has official API credentials active.</p>
        <hr style="border-color: #334155;" />
        <p style="font-size: 12px; color: #94a3b8;">Sent autonomously via Resend API</p>
    </div>
    """
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "TrustPulse-Bot/1.0"
    }
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("Response:", json.dumps(res_data, indent=2))
except Exception as e:
    print("❌ Error:", e)
    if hasattr(e, 'read'):
        print("Details:", e.read().decode())
