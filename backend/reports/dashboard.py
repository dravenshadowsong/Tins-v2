import math
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Polygon, Line, Circle, String
from reportlab.lib.styles import ParagraphStyle

def draw_compact_radar_chart(scores, width=190, height=130):
    cx = width / 2.0
    cy = height / 2.0
    r_max = 42.0
    
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
        d.add(Polygon(pts, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.5, fillColor=None))
        
    # Draw axes lines from center to 100%
    for i in range(num_domains):
        x, y = get_coords(i, 100)
        d.add(Line(cx, cy, x, y, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.5))
        
    # Draw score polygon
    score_pts = []
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        score_pts.append(x)
        score_pts.append(y)
        
    d.add(Polygon(score_pts, fillColor=colors.HexColor("#5B4CF01A"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=1.2))
    
    # Draw score vertices
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        d.add(Circle(x, y, 2.0, fillColor=colors.HexColor("#F7B731"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=0.8))
        
    # Draw labels (abbreviated)
    for i, dom in enumerate(domains):
        x, y = get_coords(i, 56)
        lbl = dom["label"]
        
        anchor = "middle"
        if x < cx - 10:
            anchor = "end"
        elif x > cx + 10:
            anchor = "start"
            
        s = String(x, y - 2.0, lbl, fontName="Helvetica-Bold", fontSize=6.0, textAnchor=anchor, fillColor=colors.HexColor("#64748B"))
        d.add(s)
        
    return d

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    table_header_style = styles.table_header_style
    table_cell_style = styles.table_cell_style
    primary_color = styles.primary_color
    border_color = styles.border_color
    light_bg = styles.light_bg
    
    integ = data["integ"]
    sorted_scores = data["sorted_scores"]
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Talent Dashboard", section_header_style))
    story.append(Paragraph("COGNITIVE TALENT DASHBOARD", h1_style))
    story.append(Spacer(1, 10))
    
    # Left Column: Domain Rankings (Strongest first)
    left_flowables = []
    
    table_data = [[
        Paragraph("<b>Domain</b>", table_header_style),
        Paragraph("<b>TSI %</b>", table_header_style),
        Paragraph("<b>Strength Level</b>", table_header_style),
        Paragraph("<b>One-line Interpretation</b>", table_header_style)
    ]]
    
    for d_key, val in sorted_scores:
        lbl = styles.DOMAINS_MAP.get(d_key, d_key)
        unique_exp = styles.DOMAIN_UNIQUE_EXPLANATIONS.get(d_key, styles.DOMAIN_UNIQUE_EXPLANATIONS["creative"])
        
        # Strength Level mapping
        if val >= 75:
            level = "<font color='#5B4CF0'><b>Strong</b></font>"
        elif val >= 50:
            level = "<font color='#00B8A9'><b>Emerging</b></font>"
        else:
            level = "<font color='#8E9BAE'><b>Exploratory</b></font>"
            
        one_liner = unique_exp["significance"]
        
        table_data.append([
            Paragraph(f"<b>{lbl}</b>", table_cell_style),
            Paragraph(f"<b>{val}%</b>", table_cell_style),
            Paragraph(level, table_cell_style),
            Paragraph(one_liner, ParagraphStyle('OneLiner', parent=styles.styles['Normal'], fontSize=7.5, leading=10))
        ])
        
    rankings_table = Table(table_data, colWidths=[1.5 * inch, 0.6 * inch, 0.9 * inch, 1.6 * inch])
    rankings_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    left_flowables.append(rankings_table)
    
    # Right Column: Radar Visual Support & Description
    right_flowables = []
    right_flowables.append(Paragraph("<b>SPECTRUM RADAR</b>", styles.section_header_style))
    right_flowables.append(Spacer(1, 5))
    
    radar = draw_compact_radar_chart(integ, width=180, height=130)
    right_flowables.append(radar)
    right_flowables.append(Spacer(1, 10))
    
    right_flowables.append(Paragraph("<b>Interpretation Notes:</b>", styles.styles['Heading5']))
    right_flowables.append(Spacer(1, 4))
    right_flowables.append(Paragraph(
        "<font size='8' color='#4A4A4A'>The radar chart displays relative cognitive preference patterns. "
        "Domain scores represent percentile rankings derived from standard logical and spatial puzzle task completions. "
        "Strongest domains are listed at the top of the table on the left.</font>",
        body_style
    ))
    
    # Outer 2-Column Table
    master_table = Table([[left_flowables, right_flowables]], colWidths=[4.6 * inch, 2.4 * inch])
    master_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(master_table)
    
    story.append(PageBreak())
