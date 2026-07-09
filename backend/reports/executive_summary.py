from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    h2_style = styles.h2_style
    italic_style = styles.italic_style
    border_color = styles.border_color
    primary_label = styles.DOMAINS_MAP.get(data["primary_domain"], data["primary_domain"])
    personalizedSnapshot = data["personalizedSnapshot"]
    secondary_domains = data["secondary_domains"]
    emerging_domains = data["emerging_domains"]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Child Snapshot", section_header_style))
    story.append(Paragraph("WHO IS THIS CHILD?", h1_style))
    story.append(Paragraph(f'"{personalizedSnapshot}"', italic_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("TALENT DOMAIN SUMMARY", h2_style))
    
    # Primary Domain Card
    t1 = Table([[
        Paragraph("<font color='#5B4CF0'><b>STRONG INDICATORS</b></font>", styles.styles['Normal']),
    ], [
        Paragraph(f"<b>{primary_label.upper()}</b>", styles.styles['Heading3']),
    ]], colWidths=[7.0 * inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEEDFE")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#5B4CF0")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t1)
    story.append(Spacer(1, 12))
    
    # Secondary Domains Card
    secondary_labels = "  |  ".join([styles.DOMAINS_MAP.get(d, d).upper() for d in secondary_domains])
    t2 = Table([[
        Paragraph("<font color='#00B8A9'><b>EMERGING INDICATORS</b></font>", styles.styles['Normal']),
    ], [
        Paragraph(f"<b>{secondary_labels or 'NONE DETECTED'}</b>", styles.styles['Heading4']),
    ]], colWidths=[7.0 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#00B8A9")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))
    
    # Emerging Domains Card
    emerging_labels = "  |  ".join([styles.DOMAINS_MAP.get(d, d).upper() for d in emerging_domains])
    t3 = Table([[
        Paragraph("<font color='#B7791F'><b>NEEDS FURTHER EXPLORATION</b></font>", styles.styles['Normal']),
    ], [
        Paragraph(f"<b>{emerging_labels or 'NONE DETECTED'}</b>", styles.styles['Heading4']),
    ]], colWidths=[7.0 * inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#F7B731")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t3)
    story.append(PageBreak())
