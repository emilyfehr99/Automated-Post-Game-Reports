#!/usr/bin/env python3
"""
Test the REAL NHL logo URLs we found
"""

import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

def test_logo_urls():
    """Test the real logo URLs"""
    print("🏒 TESTING REAL NHL LOGO URLS 🏒")
    print("=" * 50)
    
    # The REAL logo URLs we found
    logo_urls = {
        'EDM_light': 'https://assets.nhle.com/logos/nhl/svg/EDM_light.svg',
        'EDM_dark': 'https://assets.nhle.com/logos/nhl/svg/EDM_dark.svg',
        'VGK_light': 'https://assets.nhle.com/logos/nhl/svg/VGK_light.svg',
        'VGK_dark': 'https://assets.nhle.com/logos/nhl/svg/VGK_dark.svg'
    }
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    working_logos = {}
    
    for name, url in logo_urls.items():
        print(f"📥 Testing {name}: {url}")
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                content_length = len(response.content)
                print(f"   ✅ SUCCESS! Type: {content_type}, Size: {content_length} bytes")
                working_logos[name] = response.content
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()
    
    return working_logos

def convert_svg_to_png(svg_content, logo_name):
    """Convert SVG to PNG using svglib"""
    try:
        print(f"🔄 Converting {logo_name} from SVG to PNG...")
        
        # Use svglib to convert SVG to ReportLab drawing
        drawing = svg2rlg(BytesIO(svg_content))
        
        if drawing:
            # Convert to PNG
            img_buffer = BytesIO()
            renderPM.drawToFile(drawing, img_buffer, fmt='PNG', dpi=200)
            img_buffer.seek(0)
            print(f"   ✅ Successfully converted {logo_name}")
            return img_buffer
        else:
            print(f"   ❌ Failed to create drawing for {logo_name}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error converting {logo_name}: {e}")
        return None

def create_logo_report(working_logos):
    """Create a report with the real logos"""
    print("\n🏒 CREATING REPORT WITH REAL LOGOS 🏒")
    print("=" * 50)
    
    # Convert logos to PNG
    converted_logos = {}
    for name, svg_content in working_logos.items():
        png_buffer = convert_svg_to_png(svg_content, name)
        if png_buffer:
            converted_logos[name] = png_buffer
    
    if not converted_logos:
        print("❌ No logos were successfully converted")
        return
    
    # Create PDF report
    doc = SimpleDocTemplate("REAL_NHL_LOGOS_REPORT.pdf", pagesize=letter)
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'Title', parent=getSampleStyleSheet()['Heading1'],
        fontSize=24, textColor=colors.darkblue,
        alignment=TA_CENTER, spaceAfter=20
    )
    
    story.append(Paragraph("🏒 REAL NHL TEAM LOGOS 🏒", title_style))
    story.append(Spacer(1, 20))
    
    # Create logo table
    logo_data = []
    
    # Add EDM logos
    if 'EDM_light' in converted_logos and 'EDM_dark' in converted_logos:
        edm_light_img = Image(converted_logos['EDM_light'])
        edm_light_img.drawHeight = 2*inch
        edm_light_img.drawWidth = 2*inch
        
        edm_dark_img = Image(converted_logos['EDM_dark'])
        edm_dark_img.drawHeight = 2*inch
        edm_dark_img.drawWidth = 2*inch
        
        logo_data.append([edm_light_img, "Edmonton Oilers", edm_dark_img])
        logo_data.append(["Light Logo", "Team Name", "Dark Logo"])
    
    # Add VGK logos
    if 'VGK_light' in converted_logos and 'VGK_dark' in converted_logos:
        vgk_light_img = Image(converted_logos['VGK_light'])
        vgk_light_img.drawHeight = 2*inch
        vgk_light_img.drawWidth = 2*inch
        
        vgk_dark_img = Image(converted_logos['VGK_dark'])
        vgk_dark_img.drawHeight = 2*inch
        vgk_dark_img.drawWidth = 2*inch
        
        logo_data.append([vgk_light_img, "Vegas Golden Knights", vgk_dark_img])
        logo_data.append(["Light Logo", "Team Name", "Dark Logo"])
    
    if logo_data:
        logo_table = Table(logo_data, colWidths=[2*inch, 3*inch, 2*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.darkblue),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(logo_table)
        story.append(Spacer(1, 20))
    
    # Add information about the logos
    info_style = ParagraphStyle(
        'Info', parent=getSampleStyleSheet()['Normal'],
        fontSize=12, textColor=colors.black, spaceAfter=6
    )
    
    story.append(Paragraph("REAL NHL LOGO INFORMATION", getSampleStyleSheet()['Heading2']))
    story.append(Paragraph("These are the ACTUAL team logos from the NHL API:", info_style))
    story.append(Paragraph("• Downloaded directly from https://assets.nhle.com/logos/nhl/svg/", info_style))
    story.append(Paragraph("• Converted from SVG to PNG format", info_style))
    story.append(Paragraph("• Both light and dark versions available", info_style))
    story.append(Paragraph("• These are the REAL team logos, not colored circles!", info_style))
    
    # Build PDF
    doc.build(story)
    print("✅ REAL NHL LOGOS REPORT CREATED: REAL_NHL_LOGOS_REPORT.pdf")

def main():
    """Main function"""
    print("🏒 NHL REAL LOGO TESTER 🏒")
    print("=" * 30)
    
    # Test the real logo URLs
    working_logos = test_logo_urls()
    
    if working_logos:
        print(f"✅ Found {len(working_logos)} working logos!")
        create_logo_report(working_logos)
    else:
        print("❌ No working logos found")

if __name__ == "__main__":
    main()
