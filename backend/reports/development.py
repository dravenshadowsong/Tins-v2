from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

def build_roadmap_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    h2_style = styles.h2_style
    body_style = styles.body_style
    light_bg = styles.light_bg
    border_color = styles.border_color
    
    primary_label = styles.DOMAINS_MAP.get(data["primary_domain"], data["primary_domain"])
    action_plan = data.get("analysis", {}).get("action_plan") or {}
    w1 = action_plan.get("week_1") or f"Introductory hands-on exercises in the primary domain of {primary_label}."
    w2 = action_plan.get("week_2") or "Join collaborative center sessions and focus on shared peer group activities."
    w3 = action_plan.get("week_3") or f"Attempt open-ended puzzle/project challenge in {primary_label} without rigid templates."
    w4 = action_plan.get("week_4") or "Facilitator progress check-in, log milestones, and showcase child creations."

    story.append(Spacer(1, 15))
    story.append(Paragraph("30-Day Developmental Plan", section_header_style))
    story.append(Paragraph("DEVELOPMENT ROADMAP: NEXT STEPS", h1_style))
    story.append(Paragraph(f"A structured 4-week action roadmap to channelize cognitive indicators into active competencies:", body_style))
    
    roadmap_data = [
        [Paragraph("<b>Week 1: Activation</b>", body_style), Paragraph(w1, body_style)],
        [Paragraph("<b>Week 2: Collaboration</b>", body_style), Paragraph(w2, body_style)],
        [Paragraph("<b>Week 3: Challenge</b>", body_style), Paragraph(w3, body_style)],
        [Paragraph("<b>Week 4: Review</b>", body_style), Paragraph(w4, body_style)]
    ]
    roadmap_table = Table(roadmap_data, colWidths=[1.5 * inch, 5.5 * inch])
    roadmap_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (0,-1), light_bg),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(roadmap_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Nurturing Guidelines", h2_style))
    story.append(Paragraph("<b>Home Action:</b> Share this roadmap with family. Schedule short, daily periods for focused solo play or creation. Acknowledge effort over outcomes.", body_style))
    story.append(Paragraph("<b>School Action:</b> Encourage the classroom teacher to assign leadership opportunities and group tasks that align with their cognitive strengths.", body_style))

def build_pathways_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    italic_style = styles.italic_style
    card_label_style = styles.card_label_style
    primary_color = styles.primary_color
    border_color = styles.border_color
    
    child = data["child"]
    sorted_scores = data["sorted_scores"]
    top_2_keys = [x[0] for x in sorted_scores[:2]]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Exploration Pathways", section_header_style))
    story.append(Paragraph("TALENT PATHWAY SUGGESTIONS", h1_style))
    story.append(Paragraph(f"Based on {child.get('name', 'the student')}'s cognitive mapping, we recommend the following learning tracks:", body_style))
    story.append(Spacer(1, 10))
    
    for i, key in enumerate(top_2_keys):
        path_info = styles.pathways_dict.get(key, styles.pathways_dict["creative"])
        p_color = styles.DOMAIN_COLORS.get(key, primary_color)
        
        path_table_data = [
            [Paragraph(f"<b>RECOMMENDED TRACK {i+1}: {path_info['title'].upper()}</b>", card_label_style)],
            [Paragraph(path_info['desc'], body_style)]
        ]
        path_table = Table(path_table_data, colWidths=[7.0 * inch])
        path_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
            ('LINELEFT', (0,0), (0,-1), 4, p_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(path_table)
        story.append(Spacer(1, 15))
        
    story.append(Paragraph("<b>Pathway Engagement Tip:</b> Encourage child autonomy. Let them sample both tracks over the next 30 days and notice which one holds their focus longest without external rewards.", italic_style))

def build_page(story, data, styles):
    build_roadmap_page(story, data, styles)
    story.append(PageBreak())
    build_pathways_page(story, data, styles)
    story.append(PageBreak())
