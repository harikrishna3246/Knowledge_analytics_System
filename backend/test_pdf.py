from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def test_pdf_generation():
    filename = "test_output.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Topic: Test Bigram Detection")
    
    y -= 30
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "From Document:")
    
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(60, y, "• This is a point from the document.")
    y -= 18
    c.drawString(60, y, "• This is another point.")
    
    y -= 25
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Additional Explanation:")
    
    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(60, y, "• External knowledge point 1.")
    y -= 18
    c.drawString(60, y, "• External knowledge point 2.")
    
    c.save()
    
    if os.path.exists(filename):
        print(f"✅ PDF successfully generated: {filename}")
        # Optionally cleanup
        # os.remove(filename)
    else:
        print("❌ PDF generation failed.")

if __name__ == "__main__":
    test_pdf_generation()
