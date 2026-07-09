from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style
    border_color = styles.border_color
    light_bg = styles.light_bg

    story.append(Spacer(1, 10))
    story.append(Paragraph("Methodology &amp; Disclosure", section_header_style))
    story.append(Paragraph("ASSESSMENT SYSTEM METHODOLOGY", h1_style))
    story.append(Paragraph("The TINS Talent Mapping framework integrates multiple data channels to evaluate developmental indicators. The pipeline transitions through these standard stages:", body_style))
    story.append(Spacer(1, 10))
    
    # Visual Workflow Sequence
    workflow_steps = [
        ("Intake Profile", "Initial background &amp; demographic mapping."),
        ("Prior Exposure", "Familiarity audit across 8 core domains."),
        ("Talent Discovery", "Home preferences &amp; interest tracking."),
        ("Puzzle Activities", "28 interactive cognitive reasoning tasks."),
        ("Observation Logs", "Direct facilitator behavioral ratings."),
        ("AI Synthesis", "Algorithmic data normalization."),
        ("Talent Mapping", "Profiling primary &amp; secondary strengths."),
        ("Roadmap Steps", "Daily/weekly developmental roadmap.")
    ]
    
    flow_cols = []
    for title, desc in workflow_steps:
        flow_cols.append([
            Paragraph(f"<font size='7.5' color='#5B4CF0'><b>{title.upper()}</b></font>", ParagraphStyle('FTitle', parent=styles.styles['Normal'], alignment=1)),
            Spacer(1, 4),
            Paragraph(f"<font size='6.5' color='#4A4A4A'>{desc}</font>", ParagraphStyle('FDesc', parent=styles.styles['Normal'], alignment=1))
        ])
        
    # Draw as a 2-row x 4-column flow grid to prevent wrapping overload
    grid_data = [
        [Table([[x] for x in flow_cols[0]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[1]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[2]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[3]], colWidths=[1.5*inch])],
        [Table([[x] for x in flow_cols[4]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[5]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[6]], colWidths=[1.5*inch]), Paragraph("<b>&rarr;</b>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
         Table([[x] for x in flow_cols[7]], colWidths=[1.5*inch])]
    ]

    
    flow_table = Table(grid_data, colWidths=[1.5*inch, 0.3*inch, 1.5*inch, 0.3*inch, 1.5*inch, 0.3*inch, 1.5*inch])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('BACKGROUND', (4,0), (4,0), light_bg),
        ('BACKGROUND', (6,0), (6,0), light_bg),
        ('BACKGROUND', (0,1), (0,1), light_bg),
        ('BACKGROUND', (2,1), (2,1), light_bg),
        ('BACKGROUND', (4,1), (4,1), light_bg),
        ('BACKGROUND', (6,1), (6,1), light_bg),
        ('BOX', (0,0), (0,0), 0.5, border_color),
        ('BOX', (2,0), (2,0), 0.5, border_color),
        ('BOX', (4,0), (4,0), 0.5, border_color),
        ('BOX', (6,0), (6,0), 0.5, border_color),
        ('BOX', (0,1), (0,1), 0.5, border_color),
        ('BOX', (2,1), (2,1), 0.5, border_color),
        ('BOX', (4,1), (4,1), 0.5, border_color),
        ('BOX', (6,1), (6,1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 20))
    
    disc_data = [[
        Paragraph("<b>⚠️ DEVELOPMENTAL AND ASSESSMENT DISCLOSURE</b>", ParagraphStyle('GoldHeader', parent=styles.styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B7791F"))),
    ], [
        Paragraph(
            "This Talent Discovery &amp; Development Report is designed purely as an educational advisory document. "
            "It is NOT a standardized IQ test, nor does it measure fixed academic potential. "
            "Cognitive preferences and interests in childhood are highly plastic and evolve continuously with exposure, encouragement, and emotional safety. "
            "We strongly caution against using these results to label the child, restrict their educational pathways, or enforce a rigid specialization. "
            "Instead, please use this report as an invitation to offer diverse exposures, support emerging strengths, and nurture growth areas with patience.",
            body_style
        )
    ]]
    disc_table = Table(disc_data, colWidths=[7.0 * inch])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#F7B731")),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(disc_table)
