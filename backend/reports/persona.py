from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_hidden_opportunities_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    h2_style = styles.h2_style
    body_style = styles.body_style
    card_label_style = styles.card_label_style
    border_color = styles.border_color
    
    child = data["child"]
    integ = data["integ"]
    sorted_scores = data["sorted_scores"]
    untapped_potential = data["untapped_potential"]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Hidden Opportunities", section_header_style))
    story.append(Paragraph("HIDDEN COGNITIVE OPPORTUNITIES", h1_style))
    story.append(Paragraph("This section highlights high-potential domains where the child demonstrated strong problem-solving capabilities despite very limited prior exposure or access. We define these as 'Untapped Potential'.", body_style))
    
    # Untapped potential display
    if untapped_potential:
        for u_key in untapped_potential:
            u_lbl = styles.DOMAINS_MAP.get(u_key, u_key)
            u_score = integ.get(u_key, 0)
            exp_val = child.get(f"exp_{u_key}", 0)
            exp_lbl = ["Never tried it", "Tried a few times", "Sometimes", "Regularly"][exp_val]
            
            untapped_data = [
                [
                    Paragraph(f"<b>🔥 UNTAPPED POTENTIAL: {u_lbl.upper()}</b>", card_label_style),
                    Paragraph("<b>HIGH POTENTIAL &middot; LOW EXPOSURE</b>", ParagraphStyle('GoldBadge', parent=styles.styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#B7791F"), alignment=2))
                ],
                [
                    Paragraph(f"{child.get('name', 'The student')} scored an impressive <b>{u_score}%</b> in cognitive puzzles for <b>{u_lbl}</b>, despite having very limited access opportunities in the past (Exposure Preference: '{exp_lbl}'). Actionable introductory workshops are highly recommended.", body_style),
                    ""
                ]
            ]
            untapped_table = Table(untapped_data, colWidths=[4.5 * inch, 2.5 * inch])
            untapped_table.setStyle(TableStyle([
                ('SPAN', (0,1), (1,1)),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF9EE")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F7B731")),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(untapped_table)
            story.append(Spacer(1, 15))
    else:
        empty_box = Table([[
            Paragraph("🌿 <b>No Untapped Potential Flags Detected</b><br/>All high-scoring cognitive domains align with positive prior exposure records. Keep supporting current nurturing tracks.", body_style)
        ]], colWidths=[7.0 * inch])
        empty_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#00B8A9")),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 14),
        ]))
        story.append(empty_box)
        story.append(Spacer(1, 20))
        
    story.append(Paragraph("DOMAIN POTENTIAL TIERS", h2_style))
    
    # Categorize domains by tier
    strong_list = [Paragraph(f"&bull; {styles.DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if s >= 75]
    emerging_list = [Paragraph(f"&bull; {styles.DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if 50 <= s < 75]
    explore_list = [Paragraph(f"&bull; {styles.DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if s < 50]

    tiers_data = [
        [
            Paragraph("<b>Strong Potential (>=75%)</b>", card_label_style),
            Paragraph("<b>Emerging Potential (50-74%)</b>", card_label_style),
            Paragraph("<b>Further Observation (<50%)</b>", card_label_style)
        ],
        [
            strong_list or [Paragraph("None", body_style)],
            emerging_list or [Paragraph("None", body_style)],
            explore_list or [Paragraph("None", body_style)]
        ]
    ]
    tiers_table = Table(tiers_data, colWidths=[2.3 * inch, 2.3 * inch, 2.4 * inch])
    tiers_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEDFE")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(tiers_table)

def build_persona_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_label_style = styles.card_label_style
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    border_color = styles.border_color
    
    primary_domain = data["primary_domain"]
    persona = styles.PERSONAS.get(primary_domain, styles.PERSONAS["creative"])

    story.append(Spacer(1, 15))
    story.append(Paragraph("Child Persona Profile", section_header_style))
    story.append(Paragraph("CHILD COGNITIVE PERSONA", h1_style))

    # Archetype Card
    persona_card_data = [
        [Paragraph(f"<font size='44'>{persona['emoji']}</font>", styles.styles['Normal'])],
        [Paragraph(f"<b>{persona['title']}</b>", ParagraphStyle('ArcTitle', parent=styles.styles['Heading2'], textColor=primary_color, alignment=1, fontSize=16))],
        [Paragraph(persona['desc'], ParagraphStyle('ArcDesc', parent=body_style, alignment=1, fontSize=10, leading=15))]
    ]
    persona_card = Table(persona_card_data, colWidths=[7.0 * inch])
    persona_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEECFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C3C0F9")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(persona_card)
    story.append(Spacer(1, 20))
    
    # Strengths / Growth Columns
    strengths_items = [Paragraph(f"&bull; <b>{s}</b>", body_style) for s in persona["strengths"]]
    growth_items = [Paragraph(f"&bull; <b>{g}</b>", body_style) for g in persona["growth"]]
    
    columns_data = [
        [
            Paragraph("<b>PRIMARY STRENGTHS</b>", card_label_style),
            "",
            Paragraph("<b>TARGETED GROWTH AREAS</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))
        ],
        [
            strengths_items,
            "",
            growth_items
        ]
    ]
    columns_table = Table(columns_data, colWidths=[3.4 * inch, 0.2 * inch, 3.4 * inch])
    columns_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#EEEDFE")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#E2F9F6")),
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(columns_table)

def build_page(story, data, styles):
    build_hidden_opportunities_page(story, data, styles)
    story.append(PageBreak())
    build_persona_page(story, data, styles)
    story.append(PageBreak())
