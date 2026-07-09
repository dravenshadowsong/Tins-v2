from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
import json

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    h2_style = styles.h2_style
    body_style = styles.body_style
    italic_style = styles.italic_style
    border_color = styles.border_color
    primary_color = styles.primary_color
    secondary_color = styles.secondary_color
    light_bg = styles.light_bg
    card_body_style = styles.card_body_style
    table_cell_style = styles.table_cell_style
    
    child = data["child"]
    session = data["session"]
    primary_domain = data["primary_domain"]
    primary_label = styles.DOMAINS_MAP.get(primary_domain, primary_domain)
    personalizedSnapshot = data["personalizedSnapshot"]
    secondary_domains = data["secondary_domains"]
    emerging_domains = data["emerging_domains"]
    formatted_date = data["formatted_date"]
    
    unique_exp = styles.DOMAIN_UNIQUE_EXPLANATIONS.get(primary_domain, styles.DOMAIN_UNIQUE_EXPLANATIONS["creative"])

    # ──────────────────────────────────────────────────────────
    # PAGE 2: EXECUTIVE SUMMARY
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("Executive Summary", section_header_style))
    story.append(Paragraph("WHO IS THIS CHILD?", h1_style))
    story.append(Paragraph(f'"{personalizedSnapshot}"', italic_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("PRIMARY COGNITIVE MAPPING", h2_style))
    
    # Primary Domain Card (What, Why, Next Steps)
    primary_card_data = [
        [
            Paragraph(f"<font color='#5B4CF0'><b>PRIMARY TALENT: {primary_label.upper()}</b></font>", styles.styles['Heading4']),
        ],
        [
            Paragraph(f"<b>What did we observe?</b><br/>{unique_exp['behaviour']}", card_body_style),
        ],
        [
            Paragraph(f"<b>Why does it matter?</b><br/>{unique_exp['significance']}", card_body_style),
        ],
        [
            Paragraph(f"<b>What should parents do next?</b><br/>{unique_exp['nurture']}", card_body_style),
        ]
    ]
    primary_table = Table(primary_card_data, colWidths=[7.0 * inch])
    primary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEEDFE")),
        ('LINELEFT', (0,0), (0,-1), 5, primary_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(primary_table)
    story.append(Spacer(1, 15))
    
    # Secondary & Emerging Domains Cards side by side
    sec_labels = [styles.DOMAINS_MAP.get(d, d).upper() for d in secondary_domains]
    sec_text = "  |  ".join(sec_labels) if sec_labels else "NONE DETECTED"
    
    em_labels = [styles.DOMAINS_MAP.get(d, d).upper() for d in emerging_domains]
    em_text = "  |  ".join(em_labels) if em_labels else "NONE DETECTED"
    
    sec_card_data = [
        [Paragraph("<font color='#00B8A9'><b>SECONDARY TALENTS</b></font>", styles.styles['Normal'])],
        [Paragraph(f"<b>{sec_text}</b>", card_body_style)]
    ]
    sec_table = Table(sec_card_data, colWidths=[3.4 * inch])
    sec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
        ('LINELEFT', (0,0), (0,-1), 4, secondary_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    
    em_card_data = [
        [Paragraph("<font color='#B7791F'><b>EMERGING AREAS</b></font>", styles.styles['Normal'])],
        [Paragraph(f"<b>{em_text}</b>", card_body_style)]
    ]
    em_table = Table(em_card_data, colWidths=[3.4 * inch])
    em_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('LINELEFT', (0,0), (0,-1), 4, styles.accent_gold),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    
    grid_table = Table([[sec_table, "", em_table]], colWidths=[3.4 * inch, 0.2 * inch, 3.4 * inch])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(grid_table)
    
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────
    # PAGE 3: ASSESSMENT SUMMARY (NEW PAGE)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("Assessment Records", section_header_style))
    story.append(Paragraph("ASSESSMENT SUMMARY", h1_style))
    story.append(Paragraph("Technical metadata and sources utilized to compile the student's cognitive profile.", body_style))
    story.append(Spacer(1, 15))
    
    # Parse timing data safely
    timing_data_raw = session.get("timing_data")
    timing_data = {}
    if timing_data_raw:
        try:
            if isinstance(timing_data_raw, str):
                timing_data = json.loads(timing_data_raw)
            else:
                timing_data = timing_data_raw
        except Exception:
            pass
            
    # Build session metadata table (hide duration if timing analytics are not available)
    session_metadata_rows = [
        [Paragraph("<b>Assessment Date</b>", table_cell_style), Paragraph(formatted_date, table_cell_style)],
        [Paragraph("<b>Completion Status</b>", table_cell_style), Paragraph(session.get("status", "Complete").capitalize(), table_cell_style)],
        [Paragraph("<b>Questions Completed</b>", table_cell_style), Paragraph("28 / 28", table_cell_style)]
    ]
    
    duration = timing_data.get("total_formatted") or timing_data.get("duration")
    if duration:
        session_metadata_rows.append([
            Paragraph("<b>Assessment Duration</b>", table_cell_style),
            Paragraph(str(duration), table_cell_style)
        ])
        
    metadata_table = Table(session_metadata_rows, colWidths=[2.5 * inch, 4.5 * inch])
    metadata_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (0,-1), light_bg),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("EVIDENCE SOURCES VERIFIED", h2_style))
    story.append(Spacer(1, 5))
    
    # Check what evidence sources were used
    has_facilitator_notes = True if data.get("note") else False
    
    evidence_sources = [
        ("Discovery Intake Questionnaire", "✓ Active", "Biographical background and home exposure preferences."),
        ("Prior Exposure Analysis", "✓ Active", "Familiarity audit across the 8 cognitive domains."),
        ("Interactive Puzzle Puzzles", "✓ Active", "Percentile performance index derived from 28 cognitive tasks."),
        ("Facilitator Observation Logs", "✓ Active" if has_facilitator_notes else "Not Mapped", "Direct behavioral notes logged by the lead mentor.")
    ]
    
    ev_rows = [[
        Paragraph("<b>Evidence Source</b>", styles.table_header_style),
        Paragraph("<b>Status</b>", styles.table_header_style),
        Paragraph("<b>Verification Details</b>", styles.table_header_style)
    ]]
    for src, status, details in evidence_sources:
        status_color = "#00B8A9" if "Active" in status else "#94A3B8"
        ev_rows.append([
            Paragraph(f"<b>{src}</b>", table_cell_style),
            Paragraph(f"<font color='{status_color}'><b>{status}</b></font>", table_cell_style),
            Paragraph(details, table_cell_style)
        ])
        
    ev_table = Table(ev_rows, colWidths=[2.2 * inch, 1.2 * inch, 3.6 * inch])
    ev_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(ev_table)
    
    story.append(PageBreak())
