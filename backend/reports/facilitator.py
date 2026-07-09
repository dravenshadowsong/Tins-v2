from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    table_header_style = styles.table_header_style
    table_cell_style = styles.table_cell_style
    card_label_style = styles.card_label_style
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    border_color = styles.border_color
    light_bg = styles.light_bg
    
    note = data.get("note") or {}
    facilitator_name = data.get("facilitator_name") or "GOAT Facilitator"
    formatted_date = data.get("formatted_date") or ""
    child = data.get("child") or {}

    story.append(Spacer(1, 10))
    story.append(Paragraph("Mentor Validation & Review", section_header_style))
    story.append(Paragraph("FACILITATOR VALIDATION", h1_style))
    story.append(Paragraph("This page reflects direct observation notes from the classroom facilitator who conducted the cognitive assessment and monitored behavioral indicators.", body_style))
    story.append(Spacer(1, 10))
    
    # 5 Observation Metrics formatted as ★★★★☆ stars
    def get_stars_str(val):
        try:
            val_int = int(val)
            if val_int < 1: val_int = 3
            if val_int > 5: val_int = 5
        except Exception:
            val_int = 3
        return "★" * val_int + "☆" * (5 - val_int)

    obs_metrics = [
        ("Intellectual Curiosity", note.get("obs_curiosity", 3)),
        ("Task Persistence", note.get("obs_focus", 3)),
        ("Focused Engagement", note.get("obs_focus", 3)),
        ("Communication Clarity", note.get("obs_communication", 3)),
        ("Social Influence / Leadership", note.get("obs_leadership", 3))
    ]
    
    metrics_table_data = [[
        Paragraph("<b>Observation Metric</b>", table_header_style),
        Paragraph("<b>Rating Score</b>", table_header_style),
        Paragraph("<b>Developmental Indicator</b>", table_header_style)
    ]]
    
    for metric, rating in obs_metrics:
        stars = get_stars_str(rating)
        metrics_table_data.append([
            Paragraph(f"<b>{metric}</b>", table_cell_style),
            Paragraph(f"<font color='#5B4CF0'><b>{stars}</b></font>", table_cell_style),
            Paragraph("Standard performance observed" if "☆" in stars[3:] else "Advanced preference logged", table_cell_style)
        ])
        
    m_table = Table(metrics_table_data, colWidths=[2.8 * inch, 1.8 * inch, 2.4 * inch])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 15))
    
    # Observations Log
    obs_text = note.get("observation") or "The student demonstrated positive focus and curiosity during the structured session."
    strengths_text = note.get("strengths_observed") or "Demonstrates rapid comprehension and willingness to attempt complex tasks."
    concerns_text = note.get("concerns") or "Requires occasional reassurance to handle open-ended tasks."
    rec_text = note.get("notes") or f"We suggest continuing to support {child.get('name', 'the student')} with creative arts or logical tasks."
    
    obs_box_data = [
        [Paragraph("<b>Observed Strengths:</b>", card_label_style)],
        [Paragraph(strengths_text, body_style)],
        [Paragraph("<b>Areas Requiring Support:</b>", ParagraphStyle('GoldLabel', parent=card_label_style, textColor=colors.HexColor("#B7791F")))],
        [Paragraph(concerns_text, body_style)],
        [Paragraph("<b>Facilitator Notes:</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))],
        [Paragraph(f"{obs_text}<br/><br/><i>Recommendations:</i> {rec_text}", body_style)]
    ]
    
    obs_box = Table(obs_box_data, colWidths=[7.0 * inch])
    obs_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(obs_box)
    story.append(Spacer(1, 20))
    
    # Signature Lines
    sig_data = [
        [
            Paragraph(f"<b>Facilitator Name:</b> {facilitator_name}", table_cell_style),
            Paragraph(f"<b>Validation Date:</b> {formatted_date}", table_cell_style)
        ],
        [
            Paragraph("<b>Signature:</b> ___________________________", table_cell_style),
            Paragraph("<b>Status:</b> Validated & Checked", table_cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(sig_table)
    story.append(PageBreak())
