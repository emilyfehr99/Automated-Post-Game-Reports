#!/usr/bin/env python3
"""
PDF to Image Converter for NHL Post-Game Reports
Converts PDF reports to high-quality PNG images
"""

import os
import sys
from pathlib import Path
from pdf2image import convert_from_path
import argparse

def convert_pdf_to_images(pdf_path, output_dir=None, dpi=300, format='PNG'):
    """
    Convert a PDF file to images
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Output directory (defaults to same directory as PDF)
        dpi (int): DPI for the output images (default: 300)
        format (str): Output format ('PNG', 'JPEG', etc.)
    
    Returns:
        list: List of generated image file paths
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return []
    
    # Set output directory
    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Converting: {pdf_path.name}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📐 DPI: {dpi}")
    
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        generated_files = []
        
        for i, image in enumerate(images):
            # Create output filename
            base_name = pdf_path.stem
            if len(images) == 1:
                # Single page - no page number
                output_filename = f"{base_name}.{format.lower()}"
            else:
                # Multiple pages - add page number
                output_filename = f"{base_name}_page_{i+1:02d}.{format.lower()}"
            
            output_path = output_dir / output_filename
            
            # Save image
            image.save(output_path, format=format)
            generated_files.append(str(output_path))
            
            print(f"  ✅ Page {i+1}: {output_filename}")
        
        return generated_files
        
    except Exception as e:
        print(f"❌ Error converting {pdf_path.name}: {str(e)}")
        return []

def batch_convert_pdfs(input_dir, output_dir=None, dpi=300, format='PNG'):
    """
    Convert all PDF files in a directory to images
    
    Args:
        input_dir (str): Directory containing PDF files
        output_dir (str): Output directory for images
        dpi (int): DPI for the output images
        format (str): Output format
    
    Returns:
        dict: Dictionary mapping PDF files to their generated image files
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        return {}
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {input_dir}")
        return {}
    
    print(f"📁 Found {len(pdf_files)} PDF files in: {input_dir}")
    
    # Set output directory
    if output_dir is None:
        output_dir = input_dir / "images"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    total_images = 0
    
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        image_files = convert_pdf_to_images(pdf_file, output_dir, dpi, format)
        results[str(pdf_file)] = image_files
        total_images += len(image_files)
    
    print(f"\n🎯 BATCH CONVERSION COMPLETE")
    print(f"{'='*60}")
    print(f"📊 PDFs processed: {len(pdf_files)}")
    print(f"🖼️  Images generated: {total_images}")
    print(f"📁 Output directory: {output_dir}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Convert PDF files to images")
    parser.add_argument("input", help="Input PDF file or directory containing PDFs")
    parser.add_argument("-o", "--output", help="Output directory for images")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="DPI for output images (default: 300)")
    parser.add_argument("-f", "--format", default="PNG", choices=["PNG", "JPEG", "JPG"], help="Output format (default: PNG)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        # Single PDF file
        print("🔄 Converting single PDF file...")
        convert_pdf_to_images(input_path, args.output, args.dpi, args.format)
    elif input_path.is_dir():
        # Directory of PDFs
        print("🔄 Converting all PDFs in directory...")
        batch_convert_pdfs(input_path, args.output, args.dpi, args.format)
    else:
        print(f"❌ Error: {input_path} is not a valid PDF file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()

