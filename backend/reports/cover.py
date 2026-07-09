import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Spacer, PageBreak

def build_page(story, data, styles):
    # PAGE 1: COVER PAGE (Drawn in background callback)
    story.append(Spacer(1, 1))  # dummy flowable
    story.append(PageBreak())

def draw_cover_page(canvas, doc, data, styles_module):
    child = data.get("child", {})
    formatted_date = data.get("formatted_date", "")
    sid = data.get("sid", "")
    facilitator_name = data.get("facilitator_name", "")

    canvas.saveState()
    # Left indigo stripe background
    canvas.setFillColor(colors.HexColor("#5B4CF0"))
    canvas.rect(0, 0, 160, 792, fill=1, stroke=0)
    
    # Gold accent stripe
    canvas.setFillColor(colors.HexColor("#F7B731"))
    canvas.rect(160, 0, 5, 792, fill=1, stroke=0)
    
    # Concentric faint white decorative arcs
    canvas.setStrokeColor(colors.HexColor("#7C6FFE"))
    canvas.setLineWidth(1)
    canvas.circle(0, 396, 100, fill=0, stroke=1)
    canvas.circle(0, 396, 140, fill=0, stroke=1)
    canvas.circle(0, 396, 180, fill=0, stroke=1)
    
    # Project WHY Logo (parent folder of backend/reports)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    why_logo_path = os.path.join(base_dir, "why_logo.jpg")
    if os.path.exists(why_logo_path):
        canvas.drawImage(why_logo_path, 185, 685, width=30, height=30, mask='auto')
    else:
        canvas.setFillColor(colors.HexColor("#00B8A9"))
        canvas.circle(200, 700, 15, fill=1, stroke=0)
        canvas.setStrokeColor(colors.white)
        canvas.setLineWidth(2.5)
        canvas.line(200, 700, 200, 690)
        canvas.line(200, 700, 192, 708)
        canvas.line(200, 700, 208, 708)
    
    canvas.setFillColor(colors.HexColor("#2D3436"))
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(225, 696, "PROJECT WHY")
    
    # GOAT Logo next to it
    goat_logo_path = os.path.join(base_dir, "goat_logo.png")
    if os.path.exists(goat_logo_path):
        canvas.drawImage(goat_logo_path, 360, 685, width=30, height=30, mask='auto')
    else:
        canvas.setFillColor(colors.HexColor("#5B4CF0"))
        canvas.rect(360, 685, 30, 30, fill=1, stroke=0)
        canvas.setStrokeColor(colors.white)
        canvas.setLineWidth(3.0)
        canvas.line(375, 690, 375, 710)
        canvas.line(367, 710, 383, 710)
    
    canvas.setFillColor(colors.HexColor("#2D3436"))
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(400, 696, "GOAT TALENT LAB")
    
    # Report Title
    canvas.setFillColor(colors.HexColor("#5B4CF0"))
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(200, 520, "Talent Discovery &")
    canvas.drawString(200, 485, "Development Report")
    
    # Tagline
    canvas.setFillColor(colors.HexColor("#2D3436"))
    canvas.setFont("Helvetica-Oblique", 11)
    canvas.drawString(200, 455, "Understanding Potential. Building Futures.")
    
    # Thin gold divider line
    canvas.setStrokeColor(colors.HexColor("#F7B731"))
    canvas.setLineWidth(1.5)
    canvas.line(200, 435, 520, 435)
    
    # Metadata
    metadata = [
        ("STUDENT NAME", child.get("name", "N/A").upper()),
        ("AGE", f"{child.get('age', 'N/A')} YEARS"),
        ("CLASS / LEVEL", (child.get("school_year") or "N/A").upper()),
        ("ASSESSMENT DATE", formatted_date.upper()),
        ("ASSESSMENT ID", f"GOAT-SESS-{sid}"),
        ("FACILITATOR", facilitator_name.upper())
    ]
    
    y_pos = 380
    for label, val in metadata:
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(200, y_pos, label)
        
        canvas.setFillColor(colors.HexColor("#2D3436"))
        canvas.setFont("Helvetica-Bold", 10.5)
        canvas.drawString(200, y_pos - 15, val)
        
        y_pos -= 40
        
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.setFont("Helvetica-Bold", 8.0)
    canvas.drawRightString(letter[0]-54, 40, "CONFIDENTIAL & PROPRIETARY")
    canvas.restoreState()
