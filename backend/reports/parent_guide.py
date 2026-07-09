from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_label_style = styles.card_label_style
    secondary_color = styles.secondary_color
    border_color = styles.border_color
    
    child = data["child"]
    primary_domain = data["primary_domain"]
    guide = styles.parentGuides.get(primary_domain, styles.parentGuides["creative"])

    story.append(Spacer(1, 15))
    story.append(Paragraph("Parent & Mentor Guide", section_header_style))
    story.append(Paragraph("UNDERSTANDING YOUR CHILD", h1_style))
    story.append(Paragraph(f"A tailored psychological roadmap to nurture {child.get('name', 'the student')}'s cognitive and educational preferences:", body_style))
    
    # Behaviors Card
    b_items = [Paragraph(f"&bull; {b}", body_style) for b in guide["behaviors"]]
    c1 = Table([[Paragraph("<b>💡 Observed Learning Behaviors</b>", card_label_style)], [b_items]], colWidths=[7.0 * inch])
    c1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c1)
    story.append(Spacer(1, 10))
    
    # Motivators Card
    c2 = Table([[
        Paragraph("<b>🎯 Motivators & Learning Styles</b>", card_label_style),
    ], [
        Paragraph(f"Learns best in a <b>{guide['styles']}</b> format, driven by <i>{guide['motivators']}</i>.", body_style)
    ]], colWidths=[7.0 * inch])
    c2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c2)
    story.append(Spacer(1, 10))
    
    # Challenges Card
    c3 = Table([[
        Paragraph("<b>⚠️ Potential Obstacles & Challenges</b>", ParagraphStyle('GoldLabel', parent=card_label_style, textColor=colors.HexColor("#B7791F"))),
    ], [
        Paragraph(f"{guide['challenges']}. May lose interest if forced into purely repetitive drills.", body_style)
    ]], colWidths=[7.0 * inch])
    c3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#F7B731")),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c3)
    story.append(Spacer(1, 10))
    
    # Support Card
    s_items = [Paragraph(f"&bull; {s}", body_style) for s in guide["support"]]
    c4 = Table([[Paragraph("<b>🛠️ Recommended Home Nurturing Support</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))], [s_items]], colWidths=[7.0 * inch])
    c4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#00B8A9")),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c4)
    
    story.append(PageBreak())
