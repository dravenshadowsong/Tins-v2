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

    primary_domain = data["primary_domain"]
    unique_exp = styles.DOMAIN_UNIQUE_EXPLANATIONS.get(primary_domain, styles.DOMAIN_UNIQUE_EXPLANATIONS["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("Behavioural Profile", section_header_style))
    story.append(Paragraph("OBSERVED COGNITIVE BEHAVIOURS", h1_style))
    story.append(Paragraph("This profile logs behavioral observations tracked during problem-solving tasks. We map these parameters to establish learning and execution habits.", body_style))
    story.append(Spacer(1, 8))

    # 10 Behaviors list with unique supporting evidence
    behaviours = [
        ("Curious & Inquisitive", unique_exp["behaviour"], "★★★★☆"),
        ("Task Persistence", "Sustains puzzle attempts across multiple complexity steps without giving up.", "★★★★★"),
        ("Reflective Pacing", "Pauses thoughtfully before executing pattern rotations, indicating mental planning.", "★★★★☆"),
        ("Independent Method", "Formulates execution steps without requiring constant facilitator prompts.", "★★★★☆"),
        ("Collaborative Mindset", "Shares tools and collaborates in group engineering tasks.", "★★★☆☆"),
        ("Verbal Articulation", unique_exp.get("behaviour_verbal", "Explains logical patterns and choices with high vocabulary precision."), "★★★★☆"),
        ("Analytical Precision", "Verifies shape alignment before locking, keeping error rates low.", "★★★★★"),
        ("Divergent Play", "Attempts non-traditional visual layouts in creative sandbox modules.", "★★★★☆"),
        ("Steady Focus", "Maintains a uniform task speed; shows no signs of rushing or key-spamming.", "★★★★☆"),
        ("Team Leadership", "Coordinates build stages when working in collaborative peer groups.", "★★★☆☆")
    ]

    behaviour_rows = [[
        Paragraph("<b>Observed Behaviour</b>", styles.table_header_style),
        Paragraph("<b>Supporting Cognitive Evidence</b>", styles.table_header_style),
        Paragraph("<b>Confidence</b>", styles.table_header_style)
    ]]

    for name, desc, stars in behaviours:
        behaviour_rows.append([
            Paragraph(f"<b>{name}</b>", styles.table_cell_style),
            Paragraph(desc, card_body_style),
            Paragraph(f"<font color='#5B4CF0'><b>{stars}</b></font>", ParagraphStyle('StarCol', parent=styles.table_cell_style, alignment=1))
        ])

    behaviours_table = Table(behaviour_rows, colWidths=[1.8 * inch, 4.0 * inch, 1.2 * inch])
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

    # Unique persona parameters mapping
    persona_configs = {
        "creative": {
            "style": "Visual, exploratory, sandbox-style trial-and-error.",
            "comm": "Uses drawings, structural layouts, and narratives rather than prose.",
            "env": "Open-ended, sensory-rich spaces with diverse visual materials.",
            "help": "Provide drafting logs, clay kits, and design tasks without strict rules."
        },
        "logical": {
            "style": "Analytical, sequential, structured rules decoding.",
            "comm": "Uses numeric indicators, flow charts, and step sequences.",
            "env": "Quiet, predictable settings with explicit parameters.",
            "help": "Introduce coding games, logical board games, and multi-week projects."
        },
        "spatial": {
            "style": "Hands-on structural assembly and mental rotation.",
            "comm": "Uses 3D blueprints and physical coordinates.",
            "env": "Maker spaces, crafting tables, and visual workspaces.",
            "help": "Offer LEGO engineering, complex origami, and 3D modeling grids."
        },
        "social": {
            "style": "Interactive feedback and collaborative group loops.",
            "comm": "Uses descriptive spoken explanations and active verbal listening.",
            "env": "High-collaboration classrooms and group workshop roundtables.",
            "help": "Involve in peer tutoring, group design sessions, and sports roles."
        },
        "language": {
            "style": "Narrative comprehension and conceptual debate.",
            "comm": "Uses semantic vocabulary, text logs, and verbal arguments.",
            "env": "Library zones, speech clubs, and narrative classrooms.",
            "help": "Discuss complex topics together, write story diaries, and debate prompts."
        },
        "naturalist": {
            "style": "Ecosystem observation and taxonomic classification.",
            "comm": "Uses features categorization and botanical logs.",
            "env": "Nature walks, gardens, and outdoor workspaces.",
            "help": "Supply plant care tools, insect catalog sets, and nature mapping journals."
        },
        "kinesthetic": {
            "style": "Proprioceptive tactile feedback and trial-and-error tasks.",
            "comm": "Uses physical gestures, body posture, and tactile manipulation.",
            "env": "Athletic courts, dance halls, and physical craft rooms.",
            "help": "Schedule regular physical movement breaks and hand-craft tasks."
        },
        "intrapersonal": {
            "style": "Self-paced reflective goal-setting.",
            "comm": "Uses introspective writing and goal spreadsheets.",
            "env": "Isolated quiet corners with no distracting background noise.",
            "help": "Teach diary goal tracking and offer self-paced online courses."
        }
    }
    
    cfg = persona_configs.get(primary_domain, persona_configs["creative"])

    story.append(Spacer(1, 10))
    story.append(Paragraph("Persona Profile", section_header_style))
    story.append(Paragraph("CHILD COGNITIVE PERSONA", h1_style))
    story.append(Spacer(1, 10))

    # Archetype Card
    persona_card_data = [
        [
            Paragraph(f"<font size='28'>{persona['emoji']}</font>", styles.styles['Normal']),
            Paragraph(f"<b>COGNITIVE ARCHETYPE: {persona['title']}</b><br/><font color='#4A4A4A'>{persona['desc']}</font>", styles.styles['Normal'])
        ]
    ]
    persona_card = Table(persona_card_data, colWidths=[0.8 * inch, 6.2 * inch])
    persona_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEECFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C3C0F9")),
        ('LINELEFT', (0,0), (0,-1), 4, primary_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(persona_card)
    story.append(Spacer(1, 15))

    # High Density Matrix (3 Columns: Left, Spacer, Right)
    matrix_data = [
        [
            Paragraph("<b>LEARNING STYLE</b>", card_label_style),
            "",
            Paragraph("<b>COMMUNICATION STYLE</b>", card_label_style)
        ],
        [
            Paragraph(cfg["style"], card_body_style),
            "",
            Paragraph(cfg["comm"], card_body_style)
        ],
        [
            Paragraph("<b>BEST LEARNING ENVIRONMENT</b>", card_label_style),
            "",
            Paragraph("<b>NATURAL MOTIVATORS</b>", card_label_style)
        ],
        [
            Paragraph(cfg["env"], card_body_style),
            "",
            Paragraph(guide["motivators"], card_body_style)
        ],
        [
            Paragraph("<b>POSSIBLE CHALLENGES</b>", ParagraphStyle('GoldLbl', parent=card_label_style, textColor=styles.accent_gold)),
            "",
            Paragraph("<b>HOW PARENTS CAN HELP</b>", ParagraphStyle('TealLbl', parent=card_label_style, textColor=secondary_color))
        ],
        [
            Paragraph(guide["challenges"], card_body_style),
            "",
            Paragraph(cfg["help"], card_body_style)
        ]
    ]

    matrix_table = Table(matrix_data, colWidths=[3.4 * inch, 0.2 * inch, 3.4 * inch])
    matrix_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('BACKGROUND', (0,2), (0,2), light_bg),
        ('BACKGROUND', (2,2), (2,2), light_bg),
        ('BACKGROUND', (0,4), (0,4), light_bg),
        ('BACKGROUND', (2,4), (2,4), light_bg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(matrix_table)


def build_page(story, data, styles):
    build_behaviour_profile_page(story, data, styles)
    story.append(PageBreak())
    build_persona_page(story, data, styles)
    story.append(PageBreak())
