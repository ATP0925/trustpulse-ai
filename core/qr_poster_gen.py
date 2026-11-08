"""
TrustPulse AI - Printable Table-Tent & Counter QR Poster Generator
Produces high-resolution QR codes and print-ready PDF counter cards
for reception desks, checkout counters, and restaurant tables.
"""

import os
import qrcode
from pathlib import Path
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_qr_image(url: str, output_path: str) -> str:
    """Generate high-contrast QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    img.save(output_path)
    return output_path

def generate_table_tent_pdf(
    business_name: str,
    review_url: str,
    offer_text: str = "Scan to leave a quick review & receive a special thank-you perk!",
    output_pdf: str = "table_tent_poster.pdf"
) -> str:
    """
    Generates an A5-sized high-impact table-tent PDF ready for counter printing.
    """
    temp_qr_png = str(Path(output_pdf).parent / "temp_qr.png")
    generate_qr_image(review_url, temp_qr_png)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A5,
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    story = []

    biz_style = ParagraphStyle(
        'BizName',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=4
    )

    stars_style = ParagraphStyle(
        'Stars',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=20,
        textColor=colors.HexColor('#F59E0B'),
        alignment=1,
        spaceAfter=12
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#2563EB'),
        alignment=1,
        spaceAfter=8
    )

    desc_style = ParagraphStyle(
        'Desc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        leading=14,
        spaceAfter=15
    )

    footer_style = ParagraphStyle(
        'Foot',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1,
        spaceBefore=12
    )

    story.append(Paragraph(business_name, biz_style))
    story.append(Paragraph("★ ★ ★ ★ ★", stars_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Loved Your Visit?", callout_style))
    story.append(Paragraph(f"<b>Scan the QR Code</b> with your phone camera.<br/>{offer_text}", desc_style))

    # Add QR code
    qr_img = RLImage(temp_qr_png, width=2.6 * inch, height=2.6 * inch)
    qr_img.hAlign = 'CENTER'
    story.append(qr_img)
    story.append(Spacer(1, 15))

    badge_data = [[
        Paragraph("<b>Fast & Easy</b><br/>Takes under 15 seconds", ParagraphStyle('B1', parent=desc_style, fontSize=8)),
        Paragraph("<b>Google Verified</b><br/>Direct Official Review", ParagraphStyle('B2', parent=desc_style, fontSize=8)),
        Paragraph("<b>Exclusive Perk</b><br/>Unlocked on submission", ParagraphStyle('B3', parent=desc_style, fontSize=8))
    ]]
    badge_table = Table(badge_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch])
    badge_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(badge_table)

    story.append(Paragraph("Powered by TrustPulse AI • Instant Google Review Accelerator", footer_style))

    doc.build(story)

    # Clean up temp QR
    if os.path.exists(temp_qr_png):
        os.remove(temp_qr_png)

    print(f"✅ Generated Counter Poster PDF: {output_pdf}")
    return output_pdf

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "data"
    generate_table_tent_pdf(
        business_name="Dr. Smile Dental & Laser Clinic",
        review_url="http://localhost:8000/r/dr-smile-dental",
        offer_text="Scan to rate us & unlock ₹200 off your next appointment!",
        output_pdf=str(out_dir / "sample_counter_table_tent.pdf")
    )

