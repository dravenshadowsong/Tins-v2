import math
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Polygon, Line, Circle, String, Rect
from reportlab.lib.styles import ParagraphStyle

def draw_compact_radar_chart(scores, width=216, height=160):
    cx = width / 2.0
    cy = height / 2.0
    r_max = 50.0
    
    d = Drawing(width, height)
    
    domains = [
        {"key": "creative", "label": "CRE"},
        {"key": "spatial", "label": "SPA"},
        {"key": "language", "label": "LAN"},
        {"key": "social", "label": "SOC"},
        {"key": "logical", "label": "LOG"},
        {"key": "naturalist", "label": "NAT"},
        {"key": "kinesthetic", "label": "KIN"},
        {"key": "intrapersonal", "label": "INT"},
    ]
    
    num_domains = len(domains)
    
    def get_coords(idx, value):
        angle = (idx * 2 * math.pi) / num_domains - math.pi / 2
        dist = (value / 100.0) * r_max
        return cx + dist * math.cos(angle), cy + dist * math.sin(angle)
        
    # Draw concentric grid lines (25%, 50%, 75%, 100%)
    for g in [25, 50, 75, 100]:
        pts = []
        for i in range(num_domains):
            x, y = get_coords(i, g)
            pts.append(x)
            pts.append(y)
        d.add(Polygon(pts, strokeColor=colors.HexColor("#F1F5F9"), strokeWidth=0.5, fillColor=None))
        
    # Draw axes lines
    for i in range(num_domains):
        x, y = get_coords(i, 100)
        d.add(Line(cx, cy, x, y, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5))
        
    # Draw score polygon
    score_pts = []
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        score_pts.append(x)
        score_pts.append(y)
        
    d.add(Polygon(score_pts, fillColor=colors.HexColor("#4F46E516"), strokeColor=colors.HexColor("#4F46E5"), strokeWidth=1.5))
    
    # Draw score vertices
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        d.add(Circle(x, y, 2.5, fillColor=colors.HexColor("#D97706"), strokeColor=colors.HexColor("#4F46E5"), strokeWidth=0.8))
        
    # Draw labels (abbreviated for compactness)
    for i, dom in enumerate(domains):
        x, y = get_coords(i, 118)
        lbl = dom["label"]
        
        anchor = "middle"
        if x < cx - 10:
            anchor = "end"
        elif x > cx + 10:
            anchor = "start"
            
        s = String(x, y - 2.0, lbl, fontName="Helvetica-Bold", fontSize=6.5, textAnchor=anchor, fillColor=colors.HexColor("#64748B"))
        d.add(s)
        
    return d

def draw_row_progress_bar(val, width=120, height=4, color_hex="#4F46E5"):
    d = Drawing(width, height)
    # Background strip
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F1F5F9"), strokeColor=None))
    # Filled strip
    fill_width = (val / 100.0) * width
    if fill_width > 0:
        d.add(Rect(0, 0, fill_width, height, fillColor=colors.HexColor(color_hex), strokeColor=None))
    return d

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    light_bg = styles.light_bg
    border_color = styles.border_color
    
    integ = data["integ"]
    sorted_scores = data["sorted_scores"]
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("02 / COGNITIVE TALENT DASHBOARD", section_header_style))
    story.append(Paragraph("Standardized Talent Profile", h1_style))
    story.append(Spacer(1, 10))

    # Left Column (TSI progress bars ranking)
    # We will build rows of domains
    left_flowables = []
    
    # Header of domain list
    left_flowables.append(Paragraph("<b>DOMAIN RANKING &amp; COGNITIVE INDEX</b>", styles.section_header_style))
    left_flowables.append(Spacer(1, 8))
    
    domains_data = []
    for d_key, val in sorted_scores:
        lbl = styles.DOMAINS_MAP.get(d_key, d_key)
        d_color = styles.DOMAIN_COLORS.get(d_key, styles.primary_color)
        
        # Strength tier labeling
        if val >= 75:
            tier_lbl = "Strong Indicator"
        elif val >= 50:
            tier_lbl = "Emerging"
        else:
            tier_lbl = "Exploratory"
            
        bar = draw_row_progress_bar(val, width=150, height=5, color_hex=d_color.hexval())
        
        # We represent domain list as clean horizontal rows
        domains_data.append([
            Paragraph(f"<b>{lbl}</b>", styles.table_cell_style),
            bar,
            Paragraph(f"<b>{val}%</b>", styles.table_cell_style),
            Paragraph(f"<font color='#64748B' size='7'>{tier_lbl.upper()}</font>", ParagraphStyle('TierLbl', parent=styles.styles['Normal'], alignment=2))
        ])
        
    domains_table = Table(domains_data, colWidths=[1.8*inch, 2.1*inch, 0.5*inch, 1.2*inch])
    domains_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
    ]))
    left_flowables.append(domains_table)
    
    # Right Column (Radar & Metric definitions card)
    right_flowables = []
    right_flowables.append(Paragraph("<b>COMPACT SPECTRUM MAP</b>", styles.section_header_style))
    right_flowables.append(Spacer(1, 8))
    
    radar = draw_compact_radar_chart(integ, width=180, height=140)
    right_flowables.append(radar)
    right_flowables.append(Spacer(1, 15))
    
    # Metric definitions card
    def_data = [[
        Paragraph("<font color='#4F46E5'><b>METRIC REGISTER DEFINITIONS</b></font>", styles.section_header_style)
    ], [
        Paragraph(
            "<b>TSI (Talent Strength Index):</b> Normalised percentile performance across cognitive units.<br/><br/>"
            "<b>TCI (Talent Confidence Index):</b> Metric of decision pacing stability.<br/><br/>"
            "<b>TEI (Talent Exposure Index):</b> Quantity of prior practice or training opportunities.<br/><br/>"
            "<b>DPI (Development Priority Index):</b> Recommended developmental focus hierarchy.",
            styles.card_body_style
        )
    ]]
    def_table = Table(def_data, colWidths=[2.5*inch])
    def_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    right_flowables.append(def_table)
    
    # Layout 2-Column Master Table
    master_data = [[left_flowables, right_flowables]]
    # Left column is 4.3 inches, right is 2.7 inches
    master_table = Table(master_data, colWidths=[4.3*inch, 2.7*inch])
    master_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(master_table)
    
    story.append(PageBreak())
