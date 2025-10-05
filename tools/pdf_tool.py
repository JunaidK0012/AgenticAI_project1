from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os 
from langchain_core.tools import Tool,tool

@tool
def generate_pdf(filename: str, text: str) -> str:
    """
    Generate a PDF file with the given text.

    Input:
    - filename (str): Output PDF filename (e.g.:'output.pdf')
    - text (str): Content to include in the PDF

    Output:
    - Path to the generated PDF file

    When to use:
    - When user asks to create a report or export text as PDF.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica",12)
        c.drawString(100, 750, "Generated PDF:")
        c.drawString(100, 730, text)
        c.save()
        return f"PDF generated: {os.path.abspath(filename)}"
    except Exception as e:
        return f'Error generating PDF: {str(e)}'