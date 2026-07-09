from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
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

    story.append(Spacer(1, 10))
    story.append(Paragraph("11 / SYSTEM METHODOLOGY &amp; DISCLOSURE", section_header_style))
    story.append(Paragraph("The TINS Assessment Pipeline", h1_style))
    story.append(Paragraph("TINS (Talent Intelligence &amp; Nurturing System) leverages a multi-dimensional triangulation protocol to map child potential:", body_style))
    story.append(Spacer(1, 10))

    # Flow Diagram (Modern Horizontal Steps Table)
    flow_steps = [
        [
            Paragraph("<b>01 / INTAKE</b><br/><font size='6.5' color='#64748B'>Demographics</font>", styles.table_cell_style),
            Paragraph("<font color='#64748B'>&rarr;</font>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
            Paragraph("<b>02 / EXPOSURE</b><br/><font size='6.5' color='#64748B'>Prior Access</font>", styles.table_cell_style),
            Paragraph("<font color='#64748B'>&rarr;</font>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
            Paragraph("<b>03 / PUZZLES</b><br/><font size='6.5' color='#64748B'>Fluid Logic</font>", styles.table_cell_style),
            Paragraph("<font color='#64748B'>&rarr;</font>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
            Paragraph("<b>04 / TIMING</b><br/><font size='6.5' color='#64748B'>Pacing Logs</font>", styles.table_cell_style),
            Paragraph("<font color='#64748B'>&rarr;</font>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
            Paragraph("<b>05 / OBSERVE</b><br/><font size='6.5' color='#64748B'>Facilitator</font>", styles.table_cell_style),
            Paragraph("<font color='#64748B'>&rarr;</font>", ParagraphStyle('Arr', parent=styles.styles['Normal'], alignment=1)),
            Paragraph("<b>06 / REPORT</b><br/><font size='6.5' color='#4F46E5'>Nurturing Path</font>", styles.table_cell_style)
        ]
    ]
    flow_table = Table(flow_steps, colWidths=[1.0*inch, 0.2*inch, 1.0*inch, 0.2*inch, 1.0*inch, 0.2*inch, 1.0*inch, 0.2*inch, 1.0*inch, 0.2*inch, 1.0*inch])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), light_bg),
        ('BACKGROUND', (2,0), (2,0), light_bg),
        ('BACKGROUND', (4,0), (4,0), light_bg),
        ('BACKGROUND', (6,0), (6,0), light_bg),
        ('BACKGROUND', (8,0), (8,0), light_bg),
        ('BACKGROUND', (10,0), (10,0), colors.HexColor("#EEEDFE")),
        ('BOX', (0,0), (0,0), 0.5, border_color),
        ('BOX', (2,0), (2,0), 0.5, border_color),
        ('BOX', (4,0), (4,0), 0.5, border_color),
        ('BOX', (6,0), (6,0), 0.5, border_color),
        ('BOX', (8,0), (8,0), 0.5, border_color),
        ('BOX', (10,0), (10,0), 0.5, styles.primary_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 20))

    # Reference Frameworks
    ref_data = [[
        Paragraph("<b>PSYCHOMETRIC FRAMEWORK ANCHORS</b>", styles.section_header_style)
    ], [
        Paragraph(
            "The TINS mapping system draws from established scientific frameworks in cognitive psychology:<br/>"
            "&bull; <b>Gardner's Multiple Intelligences</b>: Maps domain-specific learning preferences.<br/>"
            "&bull; <b>Cattell-Horn-Carroll (CHC) Theory</b>: Underpins the fluid reasoning tasks and abstract pattern puzzles.<br/>"
            "&bull; <b>Torrance Tests of Creative Thinking (TTCT)</b>: Guides the divergent thinking and original ideation observer metrics.",
            card_body_style
        )
    ]]
    ref_table = Table(ref_data, colWidths=[7.0*inch])
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('LINELEFT', (0,0), (0,-1), 3, styles.secondary_color),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 20))

    # Scientific Disclosure
    disc_data = [[
        Paragraph("⚠️ <b>DEVELOPMENTAL AND SCIENTIFIC DISCLOSURE</b>", ParagraphStyle('GoldHeader', parent=styles.styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=styles.accent_gold)),
    ], [
        Paragraph(
            "This report is purely advisory and is designed as a tool to guide exposure and support. "
            "It does NOT represent a fixed measure of intelligence or IQ. Cognitive preferences in childhood "
            "are highly plastic and change rapidly depending on environmental opportunities, encouragement, and safe practice. "
            "We caution against labeling children or restricting their education based on these snapshots. "
            "Instead, use these indicators to broaden their horizons and nurture emerging potential with patience.",
            body_style
        )
    ]]
    disc_table = Table(disc_data, colWidths=[7.0*inch])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ('BOX', (0,0), (-1,-1), 1.5, styles.accent_gold),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(disc_table)
