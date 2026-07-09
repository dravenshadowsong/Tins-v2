from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    italic_style = styles.italic_style
    card_label_style = styles.card_label_style
    card_body_style = styles.card_body_style
    primary_color = styles.primary_color
    border_color = styles.border_color
    
    sorted_scores = data["sorted_scores"]
    evidence = data["evidence"]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Evidence Report", section_header_style))
    story.append(Paragraph("WHY THESE TALENTS WERE IDENTIFIED", h1_style))
    story.append(Paragraph("We cross-reference multiple independent psychometric indicators to establish evidence credibility. Below is the behavioral audit log for the top 2 domains:", body_style))
    story.append(Spacer(1, 5))
    
    for d_key in [x[0] for x in sorted_scores[:2]]:
        d_lbl = styles.DOMAINS_MAP.get(d_key, d_key)
        d_color = styles.DOMAIN_COLORS.get(d_key, primary_color)
        log = evidence.get(d_key, {})
        is_sufficient = log.get("has_preference") and log.get("has_behavioral") and log.get("has_performance")
        
        # Build evidence sub-table
        if is_sufficient:
            ev_table_data = [
                [
                    Paragraph("<b>👁️ Discovery Evidence</b>", card_label_style),
                    Paragraph("<b>🌱 Exposure Preference</b>", card_label_style),
                    Paragraph("<b>🎯 Performance Accuracy</b>", card_label_style)
                ],
                [
                    Paragraph(log.get("behavioral_desc", "N/A"), card_body_style),
                    Paragraph(log.get("preference_desc", "N/A"), card_body_style),
                    Paragraph(log.get("performance_desc", "N/A"), card_body_style)
                ]
            ]
            ev_table = Table(ev_table_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
            ev_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
            ]))
        else:
            ev_table = Paragraph("<i>⚠️ Additional validation observations recommended. Prior exposure or behavioral inputs were insufficient for complete independent mapping.</i>", italic_style)
            
        domain_card = Table([[
            Paragraph(f"<font color='{d_color.hexval()}'><b>{d_lbl.upper()} INDICATORS</b></font>", styles.styles['Heading4']),
        ], [
            ev_table
        ]], colWidths=[7.0 * inch])
        
        domain_card.setStyle(TableStyle([
            ('LINELEFT', (0,0), (0,-1), 4, d_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(domain_card)
        story.append(Spacer(1, 15))
        
    story.append(PageBreak())
