"""
Script to generate a sample PDF document for testing the OCR validation app.
This creates a simple PDF with discharge quantity information.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def create_sample_pdf(filename="sample_discharge_document.pdf", quantity=1234.56):
    """Create a sample PDF document with discharge quantity."""
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1.5*inch, "Discharge Report")
    
    # Document info
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 2.5*inch, "Document Number: DR-2024-001")
    c.drawString(1*inch, height - 2.8*inch, "Date: February 17, 2026")
    c.drawString(1*inch, height - 3.1*inch, "Facility: Manufacturing Plant A")
    
    # Discharge quantity section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 4*inch, "Discharge Information:")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 4.5*inch, f"Discharge Quantity: {quantity} units")
    c.drawString(1*inch, height - 4.8*inch, "Material: Chemical Solution XYZ")
    c.drawString(1*inch, height - 5.1*inch, "Batch Number: BCH-789012")
    
    # Additional info
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 6*inch, "Notes:")
    c.drawString(1*inch, height - 6.3*inch, "This is a sample document generated for testing purposes.")
    c.drawString(1*inch, height - 6.6*inch, "The discharge quantity can be validated against SAP records.")
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(1*inch, 0.5*inch, "Confidential - For Internal Use Only")
    
    c.save()
    print(f"✓ Sample PDF created: {filename}")
    print(f"  Quantity in document: {quantity}")

if __name__ == "__main__":
    # Create a few sample documents with different quantities
    create_sample_pdf("sample_discharge_document.pdf", 1234.56)
    create_sample_pdf("sample_discharge_document_2.pdf", 5678.90)
    create_sample_pdf("sample_discharge_document_3.pdf", 100.00)
    
    print("\n📄 Sample PDFs created successfully!")
    print("You can upload these files to test the OCR validation app.")
