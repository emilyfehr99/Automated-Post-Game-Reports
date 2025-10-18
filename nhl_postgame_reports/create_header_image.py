#!/usr/bin/env python3
"""
Create the modern header image for NHL post-game reports
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime

def create_header_image(game_title="Game 1: Trenton", score="5-4", result="Loss", date=None):
    """Create the modern header image with dark textured background"""
    
    # Set dimensions (letter size width = 8.5 inches, we'll use 612 points)
    width = 612
    height = 120  # Header height
    
    # Create dark textured background
    # Create base dark color
    base_color = (25, 25, 30)  # Dark charcoal
    
    # Create the image
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)
    
    # Create diagonal striped pattern
    for i in range(0, width + height, 8):
        # Draw diagonal lines
        start_x = i
        start_y = 0
        end_x = i - height
        end_y = height
        
        # Alternate between slightly lighter and darker
        if (i // 8) % 2 == 0:
            line_color = (35, 35, 40)  # Slightly lighter
        else:
            line_color = (20, 20, 25)  # Slightly darker
            
        draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=1)
    
    # Add gradient overlay for depth
    for y in range(height):
        alpha = int(255 * (1 - y / height) * 0.3)  # Fade from top
        overlay_color = (*base_color, alpha)
        draw.rectangle([0, y, width, y+1], fill=overlay_color[:3])
    
    # Add text
    try:
        # Try to use a modern font, fallback to default
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        # Fallback fonts
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Main title - "Game 1: Trenton"
    title_text = game_title
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    
    # Position title in top-left
    title_x = 30
    title_y = 20
    
    # Draw title with slight italic effect
    draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=title_font)
    
    # Subtitle - "Immediate Post Game Report (date) | score"
    if date is None:
        date = datetime.now().strftime("%m/%d/%Y")
    
    subtitle_text = f"Immediate Post Game Report ({date}) | {score}"
    subtitle_y = title_y + title_height + 10
    
    draw.text((title_x, subtitle_y), subtitle_text, fill=(180, 180, 180), font=subtitle_font)
    
    # Result - "Loss" or "Win"
    result_text = result
    result_y = subtitle_y + 25
    
    draw.text((title_x, result_y), result_text, fill=(180, 180, 180), font=subtitle_font)
    
    return img

def create_dynamic_header(game_data):
    """Create header with dynamic game information"""
    
    try:
        # Extract game information with safe defaults
        game_center = game_data.get('game_center', {})
        game_info = game_center.get('game', {})
        away_team = game_center.get('awayTeam', {})
        home_team = game_center.get('homeTeam', {})
        
        # Create game title with fallbacks
        if game_info and away_team and home_team:
            game_number = game_info.get('gamePk', '1')
            if 'playoff' in str(game_info.get('type', '')).lower():
                game_title = f"Game {game_number}: {home_team.get('abbrev', 'Home')}"
            else:
                away_abbrev = away_team.get('abbrev', 'Away')
                home_abbrev = home_team.get('abbrev', 'Home')
                game_title = f"{away_abbrev} vs {home_abbrev}"
            
            # Get scores
            away_score = away_team.get('score', 0)
            home_score = home_team.get('score', 0)
            score = f"{away_score}-{home_score}"
            
            # Determine result (simplified)
            result = "Win" if home_score > away_score else "Loss" if away_score > home_score else "Tie"
            
            # Get date
            game_date = game_info.get('gameDate', datetime.now().strftime("%Y-%m-%d"))
        else:
            # Fallback to sample data
            game_title = "Game 1: Trenton"
            score = "5-4"
            result = "Loss"
            game_date = datetime.now().strftime("%m/%d/%Y")
        
        return create_header_image(game_title, score, result, game_date)
        
    except Exception as e:
        print(f"Error creating dynamic header: {e}")
        # Return default header
        return create_header_image("Game 1: Trenton", "5-4", "Loss", datetime.now().strftime("%m/%d/%Y"))

if __name__ == "__main__":
    # Create sample header
    img = create_header_image()
    img.save("nhl_report_header.png")
    print("Header image created: nhl_report_header.png")
    
    # Create with custom data
    custom_img = create_header_image("Game 2: Edmonton", "3-2", "Win", "05/08/2025")
    custom_img.save("nhl_report_header_custom.png")
    print("Custom header image created: nhl_report_header_custom.png")
