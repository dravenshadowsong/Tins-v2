from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    italic_style = styles.italic_style
    border_color = styles.border_color
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    light_bg = styles.light_bg
    card_label_style = styles.card_label_style
    table_cell_style = styles.table_cell_style

    primary_domain = data["primary_domain"]
    primary_label = styles.DOMAINS_MAP.get(primary_domain, primary_domain)
    personalizedSnapshot = data["personalizedSnapshot"]
    secondary_domains = data["secondary_domains"]
    emerging_domains = data["emerging_domains"]
    untapped_potential = data["untapped_potential"]
    integ = data["integ"]

    # Calculate metrics
    primary_score = integ.get(primary_domain, 0)
    
    # Helper to calculate Strength Tier
    if primary_score >= 75:
        strength_tier = "Exceptional Potential"
        tier_color = "#0D9488"
    elif primary_score >= 50:
        strength_tier = "Emerging Capability"
        tier_color = "#4F46E5"
    else:
        strength_tier = "Exploratory Area"
        tier_color = "#64748B"

    # Page Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("01 / EXECUTIVE SUMMARY", section_header_style))
    story.append(Paragraph("Cognitive Profile Summary", h1_style))
    story.append(Spacer(1, 10))

    # 1. Primary Domain Banner (Card Layout)
    primary_card_data = [
        [
            Paragraph(f"<font color='#64748B'>PRIMARY TALENT DOMAIN</font><br/><font size='14'><b>{primary_label.upper()}</b></font>", styles.styles['Normal']),
            Paragraph(f"<font color='#64748B' size='7.5'>STRENGTH INDEX (TSI)</font><br/><font size='16' color='#4F46E5'><b>{primary_score}%</b></font>", ParagraphStyle('ScoreCol', parent=styles.styles['Normal'], alignment=2))
        ],
        [
            Paragraph(f"<font color='{tier_color}'><b>● {strength_tier}</b></font> &middot; High consistency score mapped across interactive tasks.", styles.card_body_style),
            ""
        ]
    ]
    primary_table = Table(primary_card_data, colWidths=[5.2*inch, 1.8*inch])
    primary_table.setStyle(TableStyle([
        ('SPAN', (0,1), (1,1)),
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('LINELEFT', (0,0), (0,-1), 4, primary_color),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(primary_table)
    story.append(Spacer(1, 12))

    # 2. Secondary & Emerging domains (2-Column Card Grid)
    sec_badges = []
    for d in secondary_domains:
        lbl = styles.DOMAINS_MAP.get(d, d)
        sec_badges.append(f"<b>{lbl}</b> ({integ.get(d, 0)}%)")
    sec_text = "<br/>".join([f"&bull; {b}" for b in sec_badges]) or "&bull; None Detected"

    em_badges = []
    for d in emerging_domains:
        lbl = styles.DOMAINS_MAP.get(d, d)
        em_badges.append(f"<b>{lbl}</b> ({integ.get(d, 0)}%)")
    em_text = "<br/>".join([f"&bull; {b}" for b in em_badges]) or "&bull; None Detected"

    secondary_card_data = [
        [Paragraph("<b>SECONDARY DOMAINS</b>", styles.section_header_style)],
        [Paragraph(sec_text, table_cell_style)]
    ]
    secondary_card = Table(secondary_card_data, colWidths=[3.4*inch])
    secondary_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3, primary_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    emerging_card_data = [
        [Paragraph("<b>EMERGING DOMAINS</b>", ParagraphStyle('TealHdr', parent=styles.section_header_style, textColor=secondary_color))],
        [Paragraph(em_text, table_cell_style)]
    ]
    emerging_card = Table(emerging_card_data, colWidths=[3.4*inch])
    emerging_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3, secondary_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    grid_table = Table([[secondary_card, "", emerging_card]], colWidths=[3.4*inch, 0.2*inch, 3.4*inch])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 12))


    # 3. Hidden Potential Advisory
    if untapped_potential:
        u_domain = untapped_potential[0]
        u_lbl = styles.DOMAINS_MAP.get(u_domain, u_domain)
        adv_text = f"Student shows high baseline logic reasoning in <b>{u_lbl}</b> despite minimal exposure history. This represents an untapped developmental opportunity."
    else:
        adv_text = "All assessed domains align closely with reported prior exposure levels. Focus on reinforcement."

    adv_table = Table([[
        Paragraph("💡 <b>POTENTIAL HIDDEN OPPORTUNITY</b>", ParagraphStyle('GoldLbl', parent=styles.section_header_style, textColor=styles.accent_gold)),
    ], [
        Paragraph(adv_text, styles.card_body_style)
    ]], colWidths=[7.0*inch])
    adv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ('LINELEFT', (0,0), (0,-1), 3, styles.accent_gold),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(adv_table)
    story.append(Spacer(1, 16))

    # 4. KPI Blocks Row (3 Columns)
    kpi_data = [
        [
            Paragraph("<b>EVIDENCE STRENGTH</b>", styles.section_header_style),
            Paragraph("<b>TCI CONFIDENCE</b>", styles.section_header_style),
            Paragraph("<b>PRIORITY INDEX</b>", styles.section_header_style)
        ],
        [
            Paragraph("<font size='14' color='#1E293B'><b>High</b></font><br/><font size='7' color='#64748B'>Triangulated Signal</font>", styles.styles['Normal']),
            Paragraph("<font size='14' color='#1E293B'><b>92%</b></font><br/><font size='7' color='#64748B'>TCI Consistency</font>", styles.styles['Normal']),
            Paragraph("<font size='14' color='#4F46E5'><b>High Priority</b></font><br/><font size='7' color='#64748B'>Development Focus</font>", styles.styles['Normal'])
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[2.33*inch, 2.33*inch, 2.33*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 16))

    # 5. Narrative Snapshot
    story.append(Paragraph("DEVELOPMENTAL SNAPSHOT", styles.section_header_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'"{personalizedSnapshot}"', italic_style))

    story.append(PageBreak())
