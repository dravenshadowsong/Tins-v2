import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas

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

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Running Page Header
            self.drawString(54, 756, "TINS TALENT DISCOVERY & DEVELOPMENT REPORT")
            self.drawRightString(letter[0]-54, 756, "PROJECT WHY / TINS")
            
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 746, letter[0]-54, 746)
            
            # Running Page Footer
            self.drawString(54, 36, "CONFIDENTIAL DEVELOPMENTAL REPORT")
            self.drawRightString(letter[0]-54, 36, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()

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
    
    # Page 2 & 3: Child Snapshot & Talent Summary, and Assessment Summary (New Page)
    executive_summary.build_page(story, data, styles)
    
    # Page 4: Talent Dashboard (Radar chart & rankings table)
    dashboard.build_page(story, data, styles)
    
    # Page 5: Evidence Summary Cards
    evidence.build_page(story, data, styles)
    
    # Page 6 & 7: Behavioural Profile & Child Cognitive Persona
    persona.build_page(story, data, styles)
    
    # Page 8: Hidden Potential Analysis
    parent_guide.build_hidden_potential_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 9: Future Skills Timeline (Development roadmap)
    development.build_page(story, data, styles)
    
    # Page 10: Parent & School Environment Guide
    parent_guide.build_parent_school_guide_page(story, data, styles)
    story.append(PageBreak())
    
    # Page 11: Facilitator Validation (conditional)
    has_facilitator_scores = False
    note = data.get("note") or {}
    for k in ["obs_creativity", "obs_communication", "obs_leadership", "obs_focus", "obs_curiosity"]:
        if note.get(k) is not None:
            has_facilitator_scores = True
            break
            
    if has_facilitator_scores:
        facilitator.build_page(story, data, styles)
        
    # Page 12: Scientific Methodology & Disclosure
    methodology.build_page(story, data, styles)
    
    # Wrapping callbacks with data and styles closures
    def draw_cover_wrapper(canvas_obj, doc_obj):
        cover.draw_cover_page(canvas_obj, doc_obj, data, styles)
        
    doc.build(
        story, 
        canvasmaker=NumberedCanvas, 
        onFirstPage=draw_cover_wrapper
    )
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
