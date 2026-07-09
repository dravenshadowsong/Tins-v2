import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib import colors

# Import all page building components
from reports import styles
from reports import cover
from reports import executive_summary
from reports import dashboard
from reports import evidence
from reports import persona
from reports import parent_guide
from reports import development
from reports import facilitator
from reports import methodology

def add_page_number(canvas, doc, data, styles_module):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.setFillColor(styles_module.slate_label)
    
    if doc.page > 1:
        # Running Page Header
        canvas.drawString(54, 756, "TINS TALENT DISCOVERY & DEVELOPMENT REPORT")
        canvas.drawRightString(letter[0]-54, 756, "PROJECT WHY / TINS")
        
        canvas.setStrokeColor(styles_module.border_color)
        canvas.setLineWidth(0.5)
        canvas.line(54, 746, letter[0]-54, 746)
        
        # Running Page Footer
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(54, 36, "CONFIDENTIAL DEVELOPMENTAL REPORT")
        canvas.drawRightString(letter[0]-54, 36, f"Page {page_num} of 12")
    canvas.restoreState()

def build_pdf_report(data):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    story = []
    
    # Page 1: Cover Page (identity information only)
    cover.build_page(story, data, styles)
    
    # Page 2: Executive Summary (One-page overview)
    executive_summary.build_page(story, data, styles)
    
    # Page 3: Talent Dashboard (Domain ranking progress bars, small radar)
    dashboard.build_page(story, data, styles)
    
    # Page 4: Evidence Dashboard (triangulated evidence cards, no paragraphs)
    evidence.build_page(story, data, styles)
    
    # Page 5: Behaviour Profile (10 observed behaviors and metrics)
    persona.build_behaviour_profile_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 6: Persona (learning/motivator/blind spot grid)
    persona.build_persona_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 7: Hidden Potential (current ability/exposure/opportunity indices)
    parent_guide.build_hidden_potential_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 8: Development Plan (30d/90d/6m/12m milestones)
    development.build_page(story, data, styles)
    
    # Page 9: Parent & School Guide (Home vs Classroom columns)
    parent_guide.build_parent_school_guide_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 10: Assessment Analytics (KPI telemetry matrix)
    facilitator.build_analytics_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 11: Facilitator Validation (observational notes narrative, signature lines)
    facilitator.build_mentor_review_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 12: System Methodology (Pipeline steps flow & disclosure warning)
    methodology.build_page(story, data, styles)
    
    # Wrapping callbacks with data and styles closures
    def draw_cover_wrapper(canvas, doc):
        cover.draw_cover_page(canvas, doc, data, styles)
        
    def add_page_number_wrapper(canvas, doc):
        add_page_number(canvas, doc, data, styles)
        
    doc.build(story, onFirstPage=draw_cover_wrapper, onLaterPages=add_page_number_wrapper)
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
