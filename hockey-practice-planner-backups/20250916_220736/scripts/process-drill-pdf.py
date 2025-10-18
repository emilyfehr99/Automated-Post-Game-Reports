#!/usr/bin/env python3
"""
Script to process drill images from PDF files and prepare them for the hockey practice planner.
This script extracts images from PDF files and saves them in a format suitable for the web application.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

def extract_images_from_pdf(pdf_path, output_dir):
    """
    Extract images from a PDF file and save them as individual image files.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory to save extracted images
    """
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        image_count = 0
        
        # Iterate through each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Get images on this page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Get the XREF of the image
                xref = img[0]
                
                # Extract the image
                pix = fitz.Pixmap(pdf_document, xref)
                
                # Convert to PIL Image if needed
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Save the image
                    image_filename = f"drill_page_{page_num + 1}_img_{img_index + 1}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    pil_image.save(image_path, "PNG")
                    
                    print(f"✅ Extracted: {image_filename}")
                    image_count += 1
                else:
                    # Convert CMYK to RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix.tobytes("png")
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Save the image
                    image_filename = f"drill_page_{page_num + 1}_img_{img_index + 1}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    pil_image.save(image_path, "PNG")
                    
                    print(f"✅ Extracted: {image_filename}")
                    image_count += 1
                
                pix = None
        
        pdf_document.close()
        print(f"\n🎉 Successfully extracted {image_count} images from {pdf_path}")
        return image_count
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return 0

def create_drill_metadata(images_dir, output_file):
    """
    Create a metadata file for the extracted drill images.
    
    Args:
        images_dir (str): Directory containing the extracted images
        output_file (str): Path to save the metadata file
    """
    import json
    from datetime import datetime
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Create metadata structure
    metadata = {
        "created_at": datetime.now().isoformat(),
        "total_drills": len(image_files),
        "drills": []
    }
    
    for i, image_file in enumerate(sorted(image_files)):
        drill_data = {
            "id": f"drill_{i + 1:03d}",
            "filename": image_file,
            "name": f"Drill {i + 1}",
            "description": f"Extracted from PDF - {image_file}",
            "category": "Custom",
            "duration": 10,  # Default duration
            "created_at": datetime.now().isoformat()
        }
        metadata["drills"].append(drill_data)
    
    # Save metadata
    with open(output_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📄 Created metadata file: {output_file}")

def main():
    """Main function to process the drill PDF."""
    
    # Check if PyMuPDF is installed
    try:
        import fitz
    except ImportError:
        print("❌ PyMuPDF is not installed. Installing...")
        os.system("pip install PyMuPDF")
        import fitz
    
    # Check if PIL is installed
    try:
        from PIL import Image
    except ImportError:
        print("❌ PIL is not installed. Installing...")
        os.system("pip install Pillow")
        from PIL import Image
    
    # Look for the PDF file
    pdf_path = "../ihs-print-1757448115819.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("   Please make sure the PDF file is in the parent directory")
        return
    
    # Set up output directory
    output_dir = "../public/drills"
    metadata_file = "../public/drills/metadata.json"
    
    print(f"📄 Processing PDF: {pdf_path}")
    print(f"📁 Output directory: {output_dir}")
    print("")
    
    # Extract images
    image_count = extract_images_from_pdf(pdf_path, output_dir)
    
    if image_count > 0:
        # Create metadata
        create_drill_metadata(output_dir, metadata_file)
        
        print(f"\n🎉 Processing complete!")
        print(f"   - Extracted {image_count} drill images")
        print(f"   - Images saved to: {output_dir}")
        print(f"   - Metadata saved to: {metadata_file}")
        print("\n💡 You can now use these drills in the Hockey Practice Planner!")
    else:
        print("❌ No images were extracted from the PDF")

if __name__ == "__main__":
    main()
