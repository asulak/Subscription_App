# services/createinvoice.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(invoice_data):
    """
    Generates a PDF invoice based on the provided invoice data.
    
    Args:
        invoice_data (dict): Dictionary containing invoice details, e.g.,
                             {
                                 "invoice_number": "INV-2024-001",
                                 "company_name": "Your Company",
                                 "customer_name": "Customer Name",
                                 "customer_address": "Customer Address",
                                 "items": [
                                     {"description": "Service 1", "amount": 100},
                                     {"description": "Service 2", "amount": 200}
                                 ],
                                 "total_amount": 300,
                                 "issue_date": "2024-01-01",
                                 "due_date": "2024-01-31"
                             }
                             
    Returns:
        BytesIO: In-memory file containing the generated PDF.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header Section
    c.setFont("Helvetica-Bold", 20)
    c.drawString(30, 750, invoice_data.get("company_name", "Company Name"))
    
    c.setFont("Helvetica", 12)
    c.drawString(30, 730, f"Invoice Number: {invoice_data.get('invoice_number', 'N/A')}")
    c.drawString(30, 715, f"Issue Date: {invoice_data.get('issue_date', str(datetime.now().date()))}")
    c.drawString(30, 700, f"Due Date: {invoice_data.get('due_date', 'N/A')}")
    
    # Customer Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, 670, "Bill To:")
    c.setFont("Helvetica", 12)
    c.drawString(30, 655, invoice_data.get("customer_name", "Customer Name"))
    c.drawString(30, 640, invoice_data.get("customer_address", "Customer Address"))
    
    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, 600, "Description")
    c.drawString(480, 600, "Amount")
    
    # Draw Line
    c.setStrokeColor(colors.black)
    c.line(30, 595, 580, 595)
    
    # Table Content
    y_position = 580
    for item in invoice_data.get("items", []):
        c.setFont("Helvetica", 12)
        c.drawString(30, y_position, item.get("description", "Item"))
        c.drawString(480, y_position, f"${item.get('amount', 0):.2f}")
        y_position -= 20

    # Total Amount
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y_position - 20, "Total:")
    c.drawString(480, y_position - 20, f"${invoice_data.get('total_amount', 0):.2f}")

    # Footer Section
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(30, 50, "Thank you for your business!")

    # Save the PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
