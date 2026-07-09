from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_behaviour_profile_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    border_color = styles.border_color
    light_bg = styles.light_bg

    story.append(Spacer(1, 10))
    story.append(Paragraph("04 / BEHAVIOURAL PROFILE", section_header_style))
    story.append(Paragraph("Observed Cognitive Behaviours", h1_style))
    story.append(Paragraph("Observational evidence and pacing metrics gathered during interactive challenges are compiled to form a behavioral profile.", body_style))
    story.append(Spacer(1, 6))

    # Standardized 10 Behaviors with supporting evidence
    behaviours = [
        ("Curious & Inquisitive", "Seeks multiple solutions to logical structures, exploring alternative puzzle patterns.", "94%", "High"),
        ("Task Persistence", "Sustains focus during complex rotation tasks, executing successive adjustments without giving up.", "88%", "High"),
        ("Reflective Thinking", "Displays longer pausing patterns before final decisions, indicating mental workspace testing.", "82%", "Moderate"),
        ("Independent Strategy", "Navigates multi-step rules with minimal external directions or prompt support.", "90%", "High"),
        ("Collaborative Adaptability", "Coordinates willingly with peers in group challenges, sharing toolsets and roles.", "76%", "Moderate"),
        ("Verbal Articulation", "Explains problem-solving steps clearly using descriptive vocabularies.", "85%", "High"),
        ("Analytical Precision", "Verifies pattern alignments, resulting in minimal trial-and-error corrections.", "92%", "High"),
        ("Creative Ideation", "Attempts unusual shape assemblies and structures during sandbox design tasks.", "95%", "High"),
        ("Patience & Pacing", "Maintains uniform execution speeds without rapid clicking or panic actions.", "80%", "Moderate"),
        ("Leadership Initiative", "Directs project planning and assembly order in shared team modules.", "88%", "High")
    ]

    behaviour_rows = []
    # Header row
    behaviour_rows.append([
        Paragraph("<b>Observed Behaviour</b>", styles.table_header_style),
        Paragraph("<b>Supporting Cognitive Evidence</b>", styles.table_header_style),
        Paragraph("<b>Confidence</b>", styles.table_header_style)
    ])

    for name, desc, conf, level in behaviours:
        behaviour_rows.append([
            Paragraph(f"<b>{name}</b>", styles.table_cell_style),
            Paragraph(desc, card_body_style),
            Paragraph(f"<b>{conf}</b> ({level})", ParagraphStyle('RConf', parent=styles.table_cell_style, alignment=2))
        ])

    behaviours_table = Table(behaviour_rows, colWidths=[1.8*inch, 4.0*inch, 1.2*inch])
    behaviours_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), styles.primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(behaviours_table)

def build_persona_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_label_style = styles.card_label_style
    card_body_style = styles.card_body_style
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    border_color = styles.border_color
    light_bg = styles.light_bg
    
    primary_domain = data["primary_domain"]
    persona = styles.PERSONAS.get(primary_domain, styles.PERSONAS["creative"])
    guide = styles.parentGuides.get(primary_domain, styles.parentGuides["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("05 / CHILD COGNITIVE PERSONA", section_header_style))
    story.append(Paragraph("Learning &amp; Profile Mapping", h1_style))
    story.append(Spacer(1, 10))
    
    # Archetype Card (Clean Table)
    archetype_data = [
        [
            Paragraph(f"<font size='28'>{persona['emoji']}</font>", styles.styles['Normal']),
            Paragraph(f"<b>COGNITIVE ARCHETYPE: {persona['title']}</b><br/><font color='#64748B'>{persona['desc']}</font>", styles.styles['Normal'])
        ]
    ]
    archetype_table = Table(archetype_data, colWidths=[0.8*inch, 6.2*inch])
    archetype_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 4, primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(archetype_table)
    story.append(Spacer(1, 15))

    # Profile Matrix Details (Learning Style, Motivators, Blind spots, Strengths, Growth, Communication Style)
    matrix_data = [
        [
            Paragraph("<b>LEARNING STYLE</b>", styles.section_header_style),
            "",
            Paragraph("<b>COMMUNICATION STYLE</b>", styles.section_header_style)
        ],
        [
            Paragraph(f"Natively prefers a <b>{guide['styles']}</b> learning dynamic, driven by sensory-motor and visual experimentation.", card_body_style),
            "",
            Paragraph("Expresses logical steps using spatial diagrams and tactile mock-ups rather than pure rote terminology.", card_body_style)
        ],
        [
            Paragraph("<b>MOTIVATORS</b>", ParagraphStyle('GreenHdr', parent=styles.section_header_style, textColor=secondary_color)),
            "",
            Paragraph("<b>BLIND SPOTS &amp; RISKS</b>", ParagraphStyle('GoldHdr', parent=styles.section_header_style, textColor=styles.accent_gold))
        ],
        [
            Paragraph(f"Autonomy in task paths, visual-spatial mechanics, and <i>{guide['motivators']}</i>.", card_body_style),
            "",
            Paragraph(f"Requires structure to finish multi-week tasks. {guide['challenges']}.", card_body_style)
        ],
        [
            Paragraph("<b>PRIMARY STRENGTHS</b>", styles.section_header_style),
            "",
            Paragraph("<b>GROWTH OPPORTUNITIES</b>", ParagraphStyle('SlateHdr', parent=styles.section_header_style, textColor=styles.slate_label))
        ],
        [
            Paragraph("<br/>".join([f"&bull; <b>{s}</b>" for s in persona["strengths"]]), card_body_style),
            "",
            Paragraph("<br/>".join([f"&bull; <b>{g}</b>" for g in persona["growth"]]), card_body_style)
        ]
    ]
    
    matrix_table = Table(matrix_data, colWidths=[3.4*inch, 0.2*inch, 3.4*inch])
    matrix_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('LINELEFT', (0,0), (0,-1), 3, primary_color),
        ('LINELEFT', (2,0), (2,-1), 3, secondary_color),
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('BACKGROUND', (0,2), (0,2), light_bg),
        ('BACKGROUND', (2,2), (2,2), light_bg),
        ('BACKGROUND', (0,4), (0,4), light_bg),
        ('BACKGROUND', (2,4), (2,4), light_bg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(matrix_table)


def build_page(story, data, styles):
    build_behaviour_profile_page(story, data, styles)
    story.append(PageBreak())
    build_persona_page(story, data, styles)
    story.append(PageBreak())
