from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate

def build_pdf(elements, output_filename="transaction_report.pdf"):
    """
    Build the PDF report using the elements created in create_report_elements()
    
    Args:
        elements: List of reportlab elements to include in the PDF
        output_filename (str): Name of the output PDF file (optional, for reference)
    
    Returns:
        bytes: The PDF file content as bytes
    """
    # Create a BytesIO buffer to store the PDF in memory
    buffer = BytesIO()
    
    # Create the document with the buffer instead of a filename
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=34,
        leftMargin=34,
        topMargin=36,
        bottomMargin=36
    )    
    
    # Build the document with the elements
    doc.build(
        elements,
        canvasmaker=NumberedCanvas
    )
    
    # Get the PDF content as bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page info to each page (Page x of y)."""
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, total_pages):
        page = self._pageNumber
        text = f"page {page} / {total_pages}"
        self.setFont("Helvetica", 9)
        self.drawRightString(A4[0] - 0.75 * cm, 0.75 * cm, text)