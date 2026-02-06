#!/usr/bin/env python3
"""
Convert new PDFs to PNG and replace old images
"""

import os
import shutil
from pathlib import Path
from pdf2image import convert_from_path

def convert_and_cleanup():
    """Convert new PDFs to PNG and replace old images"""
    
    desktop_path = Path.home() / "Desktop"
    source_dir = desktop_path / "Recent Games"
    dest_dir = desktop_path / "Recent Games Images"
    
    # Clear old images first
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
        print(f"🗑️  Cleared old images directory")
    
    dest_dir.mkdir(exist_ok=True)
    print(f"📁 Created fresh images directory: {dest_dir}")
    
    # Find all PDF files
    pdf_files = list(source_dir.glob("*.pdf"))
    print(f"🔍 Found {len(pdf_files)} PDF files to convert")
    
    successful_conversions = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"📄 Converting {i}/{len(pdf_files)}: {pdf_file.name}")
            
            # Convert PDF to PNG (first page only)
            pages = convert_from_path(pdf_file, dpi=300, fmt='PNG')
            
            if pages:
                page = pages[0]  # Only use first page
                output_name = pdf_file.stem + ".png"
                output_path = dest_dir / output_name
                
                # Optimize for Twitter
                if page.size[0] > 4096 or page.size[1] > 4096:
                    ratio = min(4096 / page.size[0], 4096 / page.size[1])
                    new_size = (int(page.size[0] * ratio), int(page.size[1] * ratio))
                    page = page.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"  📏 Resized to {new_size[0]}x{new_size[1]} for Twitter")
                
                # Save with high quality
                page.save(output_path, "PNG", optimize=True, quality=95)
                print(f"  ✅ Saved: {output_name}")
                successful_conversions += 1
            
        except Exception as e:
            print(f"  ❌ Failed to convert {pdf_file.name}: {str(e)}")
    
    # Delete the PDF folder after successful conversion
    if successful_conversions > 0:
        try:
            shutil.rmtree(source_dir)
            print(f"\n🗑️  Deleted original PDF folder: {source_dir}")
        except Exception as e:
            print(f"\n⚠️  Could not delete PDF folder: {e}")
    
    print(f"\n🎯 CONVERSION COMPLETE")
    print(f"✅ Successful conversions: {successful_conversions}")
    print(f"📁 Images saved to: {dest_dir}")
    
    return successful_conversions > 0

if __name__ == "__main__":
    print("🏒 Converting Updated Reports to PNG 🏒")
    print("=" * 45)
    
    success = convert_and_cleanup()
    
    if success:
        print("\n🎉 All reports converted with corrected shooting percentage!")
    else:
        print("\n❌ Conversion failed.")
