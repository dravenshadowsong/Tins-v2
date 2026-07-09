from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle

def build_page(story, data, styles):
    section_header_style = styles.section_header_style
    h1_style = styles.h1_style
    body_style = styles.body_style

    story.append(Spacer(1, 15))
    story.append(Paragraph("Methodology & Disclosure", section_header_style))
    story.append(Paragraph("ASSESSMENT METHODOLOGY", h1_style))
    
    methodology_text = (
        "The GOAT Talent Mapping framework integrates multiple data points to evaluate "
        "a student's developmental indicators. The framework consists of four primary stages:<br/>"
        "1. <b>Cognitive Puzzles</b>: Abstract, language-neutral puzzles to measure pattern recognition and reasoning.<br/>"
        "2. <b>Prior Exposure Logs</b>: Mappings of historical familiarity to distinguish natural preference from taught capability.<br/>"
        "3. <b>Facilitator Observation</b>: Structured classroom observations to capture behavioral indicators (focus, leadership, communication).<br/>"
        "4. <b>Integration Engine</b>: Normalization algorithms that synthesize these signals into a structured profile."
    )
    story.append(Paragraph(methodology_text, body_style))
    story.append(Spacer(1, 20))
    
    disc_data = [[
        Paragraph("<b>⚠️ DEVELOPMENTAL AND ASSESSMENT DISCLOSURE</b>", ParagraphStyle('GoldHeader', parent=styles.styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B7791F"))),
    ], [
        Paragraph(
            "This Talent Discovery & Development Report is designed purely as an educational advisory document. "
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
