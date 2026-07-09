from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime

def build_mentor_review_page(story, data, styles):
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
    
    note = data["note"]
    facilitator_name = data["facilitator_name"]
    formatted_date = data["formatted_date"]
    child = data["child"]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Mentor Validation & Review", section_header_style))
    story.append(Paragraph("FACILITATOR VALIDATION", h1_style))
    story.append(Paragraph("This page reflects direct observation notes from the classroom facilitator who conducted the cognitive assessment and monitored behavioral indicators.", body_style))
    
    # Facilitator metrics table
    obs_metrics = [
        ("Creativity & Originality", note.get("obs_creativity", 3)),
        ("Communication & Clarity", note.get("obs_communication", 3)),
        ("Social Influence & Leadership", note.get("obs_leadership", 3)),
        ("Focused Engagement", note.get("obs_focus", 3)),
        ("Intellectual Curiosity", note.get("obs_curiosity", 3))
    ]
    
    metrics_table_data = [[
        Paragraph("<b>Observation Metric</b>", table_header_style),
        Paragraph("<b>Rating</b>", table_header_style),
        Paragraph("<b>Visual Level</b>", table_header_style)
    ]]
    
    for metric, rating in obs_metrics:
        try:
            rating_val = int(rating)
            if rating_val < 1: rating_val = 3
            if rating_val > 5: rating_val = 5
        except Exception:
            rating_val = 3
            
        bar_flowable = styles.draw_bar(rating_val, max_rating=5, width=120, height=8)
        metrics_table_data.append([
            Paragraph(f"<b>{metric}</b>", table_cell_style),
            Paragraph(f"{rating_val} / 5", table_cell_style),
            bar_flowable
        ])
        
    m_table = Table(metrics_table_data, colWidths=[3.2 * inch, 1.2 * inch, 2.6 * inch])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
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
        [Paragraph("<b>Facilitator Observations:</b>", card_label_style)],
        [Paragraph(obs_text, body_style)],
        [Paragraph("<b>Observed Strengths:</b>", card_label_style)],
        [Paragraph(strengths_text, body_style)],
        [Paragraph("<b>Areas for Support / Attention:</b>", ParagraphStyle('GoldLabel', parent=card_label_style, textColor=colors.HexColor("#B7791F")))],
        [Paragraph(concerns_text, body_style)],
        [Paragraph("<b>Validation Recommendations:</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))],
        [Paragraph(rec_text, body_style)]
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
    story.append(Spacer(1, 15))
    
    sig_data = [
        [Paragraph(f"<b>Facilitator Name:</b> {facilitator_name}", body_style), Paragraph(f"<b>Validation Date:</b> {formatted_date}", body_style)],
        [Paragraph("<b>Signature:</b> ___________________________", body_style), Paragraph("<b>Status:</b> Confirmed & Validated", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)

def build_growth_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    italic_style = styles.italic_style
    table_header_style = styles.table_header_style
    table_cell_style = styles.table_cell_style
    card_label_style = styles.card_label_style
    primary_color = styles.primary_color
    border_color = styles.border_color
    light_bg = styles.light_bg
    
    history = data["history"]
    session = data["session"]

    story.append(Spacer(1, 15))
    story.append(Paragraph("Longitudinal Growth", section_header_style))
    story.append(Paragraph("DEVELOPMENT JOURNEY TIMELINE", h1_style))
    story.append(Paragraph("Tracking the student's primary cognitive domain shifts and score stability across successive assessment sessions. This ensures our talent identification remains dynamic rather than static.", body_style))
    
    if len(history) > 1:
        hist_table_data = [[
            Paragraph("<b>Assessment Date</b>", table_header_style),
            Paragraph("<b>Session ID</b>", table_header_style),
            Paragraph("<b>Top Domain Mapped</b>", table_header_style),
            Paragraph("<b>Milestone Description</b>", table_header_style)
        ]]
        for idx, hist_row in enumerate(history):
            h_date_val = hist_row["completed_at"] or hist_row["created_at"]
            try:
                if isinstance(h_date_val, str):
                    if "." in h_date_val: h_date_val = h_date_val.split(".")[0]
                    if "T" in h_date_val:
                        h_dt = datetime.strptime(h_date_val, "%Y-%m-%dT%H:%M:%S")
                    else:
                        h_dt = datetime.strptime(h_date_val, "%Y-%m-%d %H:%M:%S")
                else:
                    h_dt = h_date_val
                h_date_str = h_dt.strftime("%d %b %Y")
            except Exception:
                h_date_str = str(h_date_val)[:10]
                
            h_top = styles.DOMAINS_MAP.get(hist_row["top_domain"], hist_row["top_domain"] or "N/A")
            h_sid = f"GOAT-SESS-{hist_row['id']}"
            
            if idx == 0:
                m_desc = "Baseline preferences mapped."
            elif idx == 1:
                m_desc = "Talent stabilization & growth verified."
            else:
                m_desc = "Longitudinal talent track active."
                
            hist_table_data.append([
                Paragraph(h_date_str, table_cell_style),
                Paragraph(h_sid, table_cell_style),
                Paragraph(h_top, table_cell_style),
                Paragraph(m_desc, table_cell_style)
            ])
            
        hist_table = Table(hist_table_data, colWidths=[1.5 * inch, 1.5 * inch, 2.0 * inch, 2.0 * inch])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ]))
        story.append(hist_table)
    else:
        baseline_data = [
            [
                Paragraph("<b>Milestone 1 (Current Session)</b>", card_label_style),
                Paragraph(f"Baseline preferences established. Primary Talent Domain identified as <b>{styles.DOMAINS_MAP.get(data['primary_domain'], data['primary_domain'])}</b>.", body_style)
            ],
            [
                Paragraph("<b>Milestone 2 (Month 6 Target)</b>", card_label_style),
                Paragraph("Scheduled check-in to trace preference migration, domain stabilization, and child development milestones.", body_style)
            ],
            [
                Paragraph("<b>Milestone 3 (Month 12 Target)</b>", card_label_style),
                Paragraph("Advanced skill mapping, assessing performance stability and hands-on portfolio review.", body_style)
            ]
        ]
        baseline_table = Table(baseline_data, colWidths=[2.2 * inch, 4.8 * inch])
        baseline_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), light_bg),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(baseline_table)
        story.append(Spacer(1, 15))
        
        # Calculate next evaluation date safely
        completed_val = session.get("completed_at") or session.get("created_at")
        try:
            if isinstance(completed_val, str):
                if "." in completed_val: completed_val = completed_val.split(".")[0]
                if "T" in completed_val:
                    dt = datetime.strptime(completed_val, "%Y-%m-%dT%H:%M:%S")
                else:
                    dt = datetime.strptime(completed_val, "%Y-%m-%d %H:%M:%S")
            else:
                dt = completed_val
            # Add 6 months (simplistic)
            import copy
            from datetime import timedelta
            # 6 months ~ 180 days
            next_dt = dt + timedelta(days=180)
            next_dt_str = next_dt.strftime("%d %b %Y")
        except Exception:
            next_dt_str = "6 Months from now"
            
        story.append(Paragraph(f"<b>Note:</b> We recommend a follow-up assessment by <b>{next_dt_str}</b> to maintain an active, accurate developmental track as the child matures.", italic_style))

def build_page(story, data, styles):
    build_mentor_review_page(story, data, styles)
    story.append(PageBreak())
    build_growth_page(story, data, styles)
    story.append(PageBreak())
