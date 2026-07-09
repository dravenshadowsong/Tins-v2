import math
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Polygon, Line, Circle, String

def draw_radar_chart(scores, width=504, height=220):
    cx = width / 2.0
    cy = height / 2.0
    r_max = 80.0
    
    d = Drawing(width, height)
    
    domains = [
        {"key": "creative", "label": "Creative & Artistic"},
        {"key": "spatial", "label": "Spatial & Making"},
        {"key": "language", "label": "Communication"},
        {"key": "social", "label": "Leadership & Social Impact"},
        {"key": "logical", "label": "Logical & Analytical"},
        {"key": "naturalist", "label": "Naturalist"},
        {"key": "kinesthetic", "label": "Kinesthetic"},
        {"key": "intrapersonal", "label": "Intrapersonal"},
    ]
    
    num_domains = len(domains)
    
    def get_coords(idx, value):
        angle = (idx * 2 * math.pi) / num_domains - math.pi / 2
        dist = (value / 100.0) * r_max
        return cx + dist * math.cos(angle), cy + dist * math.sin(angle)
        
    # Draw concentric grid lines (20%, 40%, 60%, 80%, 100%)
    for g in [20, 40, 60, 80, 100]:
        pts = []
        for i in range(num_domains):
            x, y = get_coords(i, g)
            pts.append(x)
            pts.append(y)
        d.add(Polygon(pts, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.75, fillColor=None))
        
    # Draw axes lines from center to 100%
    for i in range(num_domains):
        x, y = get_coords(i, 100)
        d.add(Line(cx, cy, x, y, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.75))
        
    # Draw score polygon
    score_pts = []
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        score_pts.append(x)
        score_pts.append(y)
        
    d.add(Polygon(score_pts, fillColor=colors.HexColor("#5B4CF026"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=2.0))
    
    # Draw score vertices
    for i, dom in enumerate(domains):
        score = scores.get(dom["key"], 0)
        x, y = get_coords(i, score)
        d.add(Circle(x, y, 3.5, fillColor=colors.HexColor("#FDCB6E"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=1.2))
        
    # Draw labels
    for i, dom in enumerate(domains):
        x, y = get_coords(i, 118)
        lbl = dom["label"]
        
        anchor = "middle"
        if x < cx - 15:
            anchor = "end"
        elif x > cx + 15:
            anchor = "start"
            
        s = String(x, y - 2.5, lbl, fontName="Helvetica-Bold", fontSize=7.5, textAnchor=anchor, fillColor=colors.HexColor("#4A4A4A"))
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

    story.append(Spacer(1, 15))
    story.append(Paragraph("Psychological Talent Map", section_header_style))
    story.append(Paragraph("DYNAMIC COGNITIVE MAP", h1_style))
    story.append(Paragraph("This radar chart illustrates the student's strengths across the 8 core cognitive domains. The normalized indices indicate natural preferences rather than fixed ability levels.", body_style))
    
    chart_flowable = draw_radar_chart(integ, width=504, height=220)
    story.append(chart_flowable)
    story.append(Spacer(1, 15))
    
    # Score Table
    table_data = [[
        Paragraph("Domain", table_header_style),
        Paragraph("Strength Tier", table_header_style),
        Paragraph("Developmental Wording", table_header_style)
    ]]
    
    # Display top 5 sorted domains
    for d_key, val in sorted_scores[:5]:
        lbl = styles.DOMAINS_MAP.get(d_key, d_key)
        # Interpretation logic
        if val >= 75:
            tier = "<font color='#5B4CF0'><b>Strong Indicators</b></font>"
            desc = "Demonstrates consistent, highly accurate pattern execution and rapid responses."
        elif val >= 50:
            tier = "<font color='#00B8A9'><b>Emerging Indicators</b></font>"
            desc = "Suggests solid foundational capability; demonstrates intuitive comfort but requires further practice."
        else:
            tier = "<font color='#8E9BAE'><b>Needs Validation</b></font>"
            desc = "Represents an area with limited spontaneous indicators; would benefit from introductory exposure."
            
        table_data.append([
            Paragraph(f"<b>{lbl}</b>", table_cell_style),
            Paragraph(tier, table_cell_style),
            Paragraph(desc, table_cell_style)
        ])
        
    scores_table = Table(table_data, colWidths=[2.2 * inch, 1.5 * inch, 3.3 * inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(scores_table)
    story.append(PageBreak())
