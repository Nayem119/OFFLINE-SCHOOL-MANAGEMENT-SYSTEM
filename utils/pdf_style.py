from pathlib import Path


def draw_brand_header(pdf, title, settings, width, height):
    from reportlab.lib import colors
    pdf.setFillColor(colors.HexColor("#17324d"))
    pdf.rect(0, height - 78, width, 78, fill=1, stroke=0)
    logo = settings.get("logo_path") if settings else ""
    if logo and Path(logo).exists():
        try:
            pdf.drawImage(str(logo), 36, height - 68, 48, 48, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
    left = 96 if logo and Path(logo).exists() else 38
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(left, height - 34, (settings.get("school_name") or "School Management System")[:70])
    pdf.setFont("Helvetica", 8)
    contact = "  |  ".join(filter(None, [settings.get("school_address"), settings.get("phone"), settings.get("email")]))
    pdf.drawString(left, height - 50, contact[:120])
    pdf.setFillColor(colors.HexColor("#2a9d8f"))
    pdf.rect(0, height - 84, width, 6, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#17324d"))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(38, height - 112, title[:90])
    return height - 132


def draw_footer(pdf, width):
    from datetime import datetime
    from reportlab.lib import colors
    pdf.setStrokeColor(colors.HexColor("#dce5ea"))
    pdf.line(38, 34, width - 38, 34)
    pdf.setFillColor(colors.HexColor("#5d7180"))
    pdf.setFont("Helvetica", 7)
    pdf.drawString(38, 22, "Generated offline  |  School Management System")
    pdf.drawRightString(width - 38, 22, datetime.now().strftime("%d %b %Y %I:%M %p"))


def draw_photo(pdf, path, x, y, size=76):
    from pathlib import Path
    if not path or not Path(path).exists():
        return False
    try:
        pdf.drawImage(str(path), x, y, size, size, preserveAspectRatio=True, anchor="c", mask="auto")
        return True
    except Exception:
        return False
