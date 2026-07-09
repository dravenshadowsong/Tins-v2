from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    card_body_style = styles.card_body_style
    border_color = styles.border_color
    light_bg = styles.light_bg

    primary_label = styles.DOMAINS_MAP.get(data["primary_domain"], data["primary_domain"])
    action_plan = data.get("analysis", {}).get("action_plan") or {}
    
    # Safely retrieve AI roadmap steps or use professional defaults
    w1 = action_plan.get("week_1") or f"Introductory sandbox projects. Provide simple non-structured material sets in the {primary_label} domain."
    w2 = action_plan.get("week_2") or "Structured tasks with group collaborators. Practice taking turns and sharing task coordination responsibilities."
    w3 = action_plan.get("week_3") or "Complex multi-step puzzles. Build self-guided checks to minimize trial-and-error clicks."
    w4 = action_plan.get("week_4") or "Facilitator progress check. Review milestones, log achievements, and showcase child creations."

    story.append(Spacer(1, 10))
    story.append(Paragraph("07 / CHRONOLOGICAL DEVELOPMENT ROADMAP", section_header_style))
    story.append(Paragraph("Chronological Development Plan", h1_style))
    story.append(Paragraph("A sequential timeline to guide the child's cognitive development from initial exposure to advanced portfolio building and reassessment.", body_style))
    story.append(Spacer(1, 10))

    # Timeline Stages: 30 Days, 90 Days, 6 Months, 12 Months
    timeline_stages = [
        ("30 DAYS", "INITIAL ACTIVATION & EXPOSURE", w1, "Increased interest in primary domains; comfortable navigating baseline puzzle environments."),
        ("90 DAYS", "STRUCTURED SKILL ACQUISITION", w2, "Ability to coordinate solutions in peer groups; improved patience during hard tasks."),
        ("6 MONTHS", "ADVANCED PROJECT BUILDING", w3, "Independent planning of complex assemblies; creation of simple personal projects."),
        ("12 MONTHS", "REASSESSMENT & RE-ALIGNMENT", w4, "Full profile reassessment to trace cognitive pattern growth and domain stability.")
    ]

    timeline_rows = []
    for timeframe, goal, activities, outcomes in timeline_stages:
        left_cell = [
            Spacer(1, 8),
            Paragraph(f"<font size='12' color='#4F46E5'><b>{timeframe}</b></font>", ParagraphStyle('TimeCenter', parent=styles.styles['Normal'], alignment=1)),
            Spacer(1, 8)
        ]
        
        right_cell = [
            Paragraph(f"<b>{goal}</b>", styles.table_cell_style),
            Paragraph(f"<b>Action Path:</b> {activities}", card_body_style),
            Paragraph(f"<b>Expected Outcome:</b> {outcomes}", ParagraphStyle('ItalicOut', parent=card_body_style, fontName='Helvetica-Oblique'))
        ]
        
        timeline_rows.append([left_cell, right_cell])

    timeline_table = Table(timeline_rows, colWidths=[1.3*inch, 5.7*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(timeline_table)
    
    story.append(PageBreak())
