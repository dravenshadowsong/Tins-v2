import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
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
    canvas.setFont('Helvetica', 8.5)
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    
    if doc.page > 1:
        canvas.drawString(54, 750, "GOAT TALENT IDENTIFICATION SYSTEM REPORT")
        canvas.drawRightString(letter[0]-54, 750, "PROJECT WHY / GOAT")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(54, 742, letter[0]-54, 742)
        
        page_num = canvas.getPageNumber()
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
    
    # Page 1: Cover Page
    cover.build_page(story, data, styles)
    
    # Page 2: Child Snapshot & Talent Summary
    executive_summary.build_page(story, data, styles)
    
    # Page 3: Psychological Talent Map (Radar chart & scorecard table)
    dashboard.build_page(story, data, styles)
    
    # Page 4: Evidence Report
    evidence.build_page(story, data, styles)
    
    # Page 5 & 6: Hidden Opportunities & Child Cognitive Persona
    persona.build_page(story, data, styles)
    
    # Page 7: Parent & Mentor Guide
    parent_guide.build_page(story, data, styles)
    
    # Page 8 & 9: 30-Day Development Roadmap & Exploration Pathways
    development.build_page(story, data, styles)
    
    # Page 10 & 11: Facilitator Validation & Longitudinal Growth
    facilitator.build_page(story, data, styles)
    
    # Page 12: Methodology & Disclosure
    methodology.build_page(story, data, styles)
    
    # Wrapping callbacks with data and styles closures
    def draw_cover_wrapper(canvas, doc):
        cover.draw_cover_page(canvas, doc, data, styles)
        
    def add_page_number_wrapper(canvas, doc):
        add_page_number(canvas, doc, data, styles)
        
    doc.build(story, onFirstPage=draw_cover_wrapper, onLaterPages=add_page_number_wrapper)
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
