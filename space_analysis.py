#!/usr/bin/env python3
"""
Space Analysis for One-Page NHL Report
Calculate exact dimensions and placement to prevent overlapping
"""

def analyze_pdf_space():
    """Analyze PDF space and calculate element dimensions"""
    
    print("📐 PDF SPACE ANALYSIS")
    print("=" * 50)
    
    # PDF dimensions
    pdf_width = 8.5  # inches
    pdf_height = 11.0  # inches
    margin = 0.2  # inches
    
    # Available space
    available_width = pdf_width - (2 * margin)
    available_height = pdf_height - (2 * margin)
    
    print(f"PDF Size: {pdf_width}\" x {pdf_height}\"")
    print(f"Margins: {margin}\" all sides")
    print(f"Available Space: {available_width}\" x {available_height}\"")
    print()
    
    # Title section
    title_height = 0.4  # 18pt font + spacing
    game_info_height = 0.3  # 8pt font + spacing
    title_section_height = title_height + game_info_height + 0.1  # 0.8" total
    
    print("📝 TITLE SECTION")
    print(f"Title: 0.4\" (18pt font)")
    print(f"Game Info: 0.3\" (8pt font)")
    print(f"Total Title Height: {title_section_height}\"")
    print()
    
    # Top section - 4 columns
    top_section_height = 2.5  # Estimated height for top section
    col_width = available_width / 4  # 2.025" each
    
    print("🏆 TOP SECTION (4 columns)")
    print(f"Column Width: {col_width:.3f}\" each")
    print(f"Estimated Height: {top_section_height}\"")
    print()
    
    # Column 1: Team Matchup
    print("Column 1 - Team Matchup:")
    print(f"  Header: 0.2\" (10pt font)")
    print(f"  Table: 1.8\" (2.2\" wide x 1.8\" tall)")
    print(f"  Total: 2.0\"")
    print()
    
    # Column 2: Team Stats
    print("Column 2 - Team Stats:")
    print(f"  Header: 0.2\" (10pt font)")
    print(f"  Table: 2.0\" (10 rows x 0.2\" per row)")
    print(f"  Total: 2.2\"")
    print()
    
    # Column 3: Shot Visualization
    print("Column 3 - Shot Visualization:")
    print(f"  Header: 0.2\" (10pt font)")
    print(f"  Chart: 1.8\" (2.2\" wide x 1.8\" tall)")
    print(f"  Total: 2.0\"")
    print()
    
    # Column 4: Top 6 Players
    print("Column 4 - Top 6 Players:")
    print(f"  Header: 0.2\" (10pt font)")
    print(f"  Table: 1.8\" (7 rows x 0.25\" per row)")
    print(f"  Total: 2.0\"")
    print()
    
    # Bottom section
    bottom_section_height = 6.0  # Remaining space
    bottom_header_height = 0.3  # 10pt font + spacing
    player_table_height = bottom_section_height - bottom_header_height  # 5.7"
    
    print("⭐ BOTTOM SECTION")
    print(f"Header: {bottom_header_height}\" (10pt font)")
    print(f"Player Table: {player_table_height}\" (16 rows)")
    print(f"Total Bottom Height: {bottom_section_height}\"")
    print()
    
    # Total height calculation
    total_height = title_section_height + top_section_height + bottom_section_height
    print("📊 TOTAL HEIGHT CALCULATION")
    print(f"Title Section: {title_section_height}\"")
    print(f"Top Section: {top_section_height}\"")
    print(f"Bottom Section: {bottom_section_height}\"")
    print(f"Total: {total_height}\"")
    print(f"Available: {available_height}\"")
    print(f"Overflow: {total_height - available_height:.2f}\"")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    if total_height > available_height:
        print("❌ OVERFLOW DETECTED!")
        print("Need to reduce heights:")
        print(f"  - Reduce top section by {total_height - available_height:.2f}\"")
        print(f"  - Or reduce bottom section by {total_height - available_height:.2f}\"")
    else:
        print("✅ HEIGHT OK - No overflow")
    
    print()
    print("🎯 OPTIMAL LAYOUT")
    print("1. Title: 0.8\" (0.4\" + 0.3\" + 0.1\" spacing)")
    print("2. Top Section: 2.0\" (4 columns of 2.025\" each)")
    print("3. Bottom Section: 5.8\" (remaining space)")
    print("4. Total: 8.6\" (fits in 10.6\" available)")

if __name__ == "__main__":
    analyze_pdf_space()
