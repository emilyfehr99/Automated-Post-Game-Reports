#!/usr/bin/env python3
"""
Simple test to verify the crumpled paper background works
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus.flowables import Flowable
from reportlab.lib.utils import ImageReader
import os

class BackgroundFlowable(Flowable):
    """Custom flowable to draw background image covering entire page"""
    def __init__(self, image_path):
        self.image_path = image_path
        # Set dimensions to cover entire letter page (8.5" x 11")
        self.width = 612  # 8.5 inches * 72 points/inch
        self.height = 792  # 11 inches * 72 points/inch
        self.drawWidth = self.width
        self.drawHeight = self.height
        Flowable.__init__(self)
    
    def draw(self):
        """Draw the background image covering the entire page"""
        if os.path.exists(self.image_path):
            img = ImageReader(self.image_path)
            # Draw image covering entire page (0, 0 to full width/height)
            self.canv.drawImage(img, 0, 0, width=self.width, height=self.height)

def create_simple_test():
    """Create a simple PDF with just the background and some text"""
    
    # Output filename - save to desktop
    output_filename = "/Users/emilyfehr8/Desktop/simple_background_test.pdf"
    
    # Create document
    doc = SimpleDocTemplate(output_filename, pagesize=letter, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create story
    story = []
    
    # Add background
    background_path = "/Users/emilyfehr8/Desktop/Paper.png"
    if os.path.exists(background_path):
        background = BackgroundFlowable(background_path)
        story.append(background)
        print(f"✅ Added crumpled paper background from: {background_path}")
    else:
        print(f"❌ Background image not found at: {background_path}")
        return
    
    # Add some test content
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("NHL Post-Game Report Test", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Dallas Stars @ St. Louis Blues", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("This is a test of the crumpled paper background.", styles['Normal']))
    story.append(Paragraph("The background should cover the entire 8.5 x 11 inch page.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Final Score: DAL 3 - STL 2", styles['Heading2']))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ Simple test PDF created: {output_filename}")
        
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"📄 File size: {file_size:,} bytes")
            print(f"📁 Full path: {os.path.abspath(output_filename)}")
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_simple_test()
