import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    child = data.get("child", {})
    formatted_date = data.get("formatted_date", "")
    sid = data.get("sid", "")
    facilitator_name = data.get("facilitator_name", "")
    session = data.get("session", {})
    
    # 1. Spacer at top
    story.append(Spacer(1, 40))
    
    # 2. Centered Logos
    base_dir = os.path.dirname(os.path.dirname(__file__))
    why_logo_path = os.path.join(base_dir, "why_logo.jpg")
    goat_logo_path = os.path.join(base_dir, "goat_logo.png")
    
    # We will build a clean header table for logos
    logo_cells = []
    if os.path.exists(why_logo_path):
        from reportlab.platypus import Image
        logo_cells.append(Image(why_logo_path, width=0.35*inch, height=0.35*inch))
    else:
        logo_cells.append(Paragraph("<b>PROJECT WHY</b>", styles.section_header_style))
        
    logo_cells.append(Paragraph("<font color='#64748B' size='14'>|</font>", styles.styles['Normal']))
    
    if os.path.exists(goat_logo_path):
        from reportlab.platypus import Image
        logo_cells.append(Image(goat_logo_path, width=0.35*inch, height=0.35*inch))
    else:
        logo_cells.append(Paragraph("<b>GOAT LAB</b>", styles.section_header_style))
        
    header_table = Table([[logo_cells[0], logo_cells[1], logo_cells[2]]], colWidths=[1.8*inch, 0.4*inch, 1.8*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 60))
    
    # 3. Report Title & Subtitle
    story.append(Paragraph("TALENT INTELLIGENCE & NUTURING SYSTEM", styles.section_header_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Talent Discovery &amp; Development Report", styles.title_style))
    story.append(Paragraph("Standardized Psychometric &amp; Cognitive Potential Profile", styles.italic_style))
    story.append(Spacer(1, 60))
    
    # 4. Thin divider line
    line_table = Table([[""]], colWidths=[7.0*inch], rowHeights=[1])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1, styles.border_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 30))
    
    # 5. Metadata Grid (3x2 Grid, Clean & Minimal)
    metadata_data = [
        [
            Paragraph("<b>STUDENT PROFILE</b>", styles.section_header_style),
            Paragraph("<b>ASSESSMENT METRICS</b>", styles.section_header_style),
            Paragraph("<b>CERTIFICATION</b>", styles.section_header_style)
        ],
        [
            Paragraph(f"<b>Name:</b> {child.get('name', 'N/A')}<br/><b>Age:</b> {child.get('age', 'N/A')} Years<br/><b>Class:</b> {child.get('school_year') or 'N/A'}", styles.table_cell_style),
            Paragraph(f"<b>ID:</b> TINS-S{sid}<br/><b>Date:</b> {formatted_date}<br/><b>Version:</b> Report v5.0", styles.table_cell_style),
            Paragraph(f"<b>Facilitator:</b> {facilitator_name}<br/><b>Status:</b> Verified Record<br/><b>Authority:</b> GOAT Labs", styles.table_cell_style)
        ]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2.33*inch, 2.33*inch, 2.33*inch])
    metadata_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BOTTOMPADDING', (0,1), (-1,1), 12),
        ('TOPPADDING', (0,1), (-1,1), 4),
        ('BOX', (0,0), (-1,-1), 0.5, styles.border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, styles.border_color),
        ('BACKGROUND', (0,0), (-1,-1), styles.light_bg),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 80))
    
    # 6. Verification block at bottom
    ver_data = [[
        Paragraph("<font color='#64748B'><b>REPORT VERIFICATION</b><br/>This document is cryptographically certified. Scan the QR verification placeholder to authenticate the assessment session records and raw psychometric scoring telemetry.</font>", styles.card_body_style),
        Paragraph("<font size='8' color='#64748B'><b>[ SECURE QR ]</b></font>", ParagraphStyle('QRLabel', parent=styles.styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#64748B"), alignment=1))
    ]]
    ver_table = Table(ver_data, colWidths=[5.4*inch, 1.6*inch])
    ver_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, styles.border_color),
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(ver_table)
    
    story.append(PageBreak())

def draw_cover_page(canvas, doc, data, styles_module):
    # Minimal running background callback - keeps the background completely white
    canvas.saveState()
    # Simple thin top gold divider accent on the cover
    canvas.setStrokeColor(styles_module.accent_gold)
    canvas.setLineWidth(1.5)
    canvas.line(54, 750, letter[0]-54, 750)
    
    canvas.setFillColor(styles_module.slate_label)
    canvas.setFont("Helvetica-Bold", 8.0)
    canvas.drawRightString(letter[0]-54, 40, "CONFIDENTIAL & STANDARDIZED PSYCHOMETRIC RECORD")
    canvas.restoreState()
