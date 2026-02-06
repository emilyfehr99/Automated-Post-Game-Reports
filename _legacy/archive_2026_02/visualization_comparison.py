#!/usr/bin/env python3
"""
Visualization Comparison - Generate PDF showing all 6 visualization options
for the game state metrics (Win Streak, Comeback Wins, Scoring First Record)
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Circle, Rect, String, Group
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
import os
import tempfile
import subprocess

def create_comparison_pdf():
    """Create PDF showing all 6 visualization options"""
    
    # Create temp file
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, "visualization_comparison.pdf")
    
    # Sample data for display
    sample_stats = {
        'current_streak': {'type': 'win', 'count': 3},
        'comeback_wins': 4,
        'scored_first_wins': 8,
        'scored_first_losses': 2,
    }
    
    scored_first_pct = (sample_stats['scored_first_wins'] / (sample_stats['scored_first_wins'] + sample_stats['scored_first_losses']) * 100) if (sample_stats['scored_first_wins'] + sample_stats['scored_first_losses']) > 0 else 0.0
    streak_text = f"W{sample_stats['current_streak']['count']}"
    comeback_wins = sample_stats['comeback_wins']
    
    # Create PDF
    doc = BaseDocTemplate(output_file, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    from reportlab.platypus.frames import Frame
    from reportlab.platypus import PageTemplate
    
    frame = Frame(72, 72, 468, 648, id='normal')
    page_template = PageTemplate(id='normal', frames=[frame])
    doc.addPageTemplates([page_template])
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    story.append(Paragraph("Visualization Options - Game State Metrics", styles['Title']))
    story.append(Spacer(1, 20))
    
    # Option 1: Badge/Card Style with Icons
    story.append(Paragraph("<b>Option 1: Badge/Card Style with Icons</b>", styles['Heading2']))
    
    class BadgeFlowable(Flowable):
        def __init__(self, icon_text, number, label, color):
            Flowable.__init__(self)
            self.icon_text = icon_text
            self.number = number
            self.label = label
            self.color = color
            self.width = 0.6 * inch
            self.height = 0.8 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            # Draw rounded rectangle background
            self.canv.setStrokeColor(self.color)
            self.canv.setFillColor(colors.white)
            self.canv.setLineWidth(2)
            self.canv.roundRect(0, 0, self.width, self.height, 5, stroke=1, fill=1)
            
            # Draw icon (simulated with text)
            self.canv.setFillColor(self.color)
            self.canv.setFont("Helvetica-Bold", 20)
            self.canv.drawCentredString(self.width/2, self.height - 0.35*inch, self.icon_text)
            
            # Draw number
            self.canv.setFont("Helvetica-Bold", 16)
            self.canv.drawCentredString(self.width/2, self.height - 0.55*inch, str(self.number))
            
            # Draw label
            self.canv.setFont("Helvetica", 8)
            self.canv.setFillColor(colors.black)
            self.canv.drawCentredString(self.width/2, 0.1*inch, self.label)
            
            self.canv.restoreState()
    
    # Create three badges side by side
    badge_table_data = [[
        BadgeFlowable("🔥", streak_text, "STREAK", colors.Color(255/255, 140/255, 0/255)),
        BadgeFlowable("⬆️", comeback_wins, "COMEBACKS", colors.Color(34/255, 139/255, 34/255)),
        BadgeFlowable("🎯", f"{scored_first_pct:.0f}%", "SCORE 1ST", colors.Color(30/255, 144/255, 255/255))
    ]]
    badge_table = Table(badge_table_data, colWidths=[0.7*inch, 0.7*inch, 0.7*inch])
    badge_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 30))
    
    # Option 2: Mini Circular Gauges
    story.append(Paragraph("<b>Option 2: Mini Circular Gauges</b>", styles['Heading2']))
    
    class CircularGauge(Flowable):
        def __init__(self, value, max_value, label, color):
            Flowable.__init__(self)
            self.value = value
            self.max_value = max(max_value, value, 10)  # Ensure max is reasonable
            self.label = label
            self.color = color
            self.width = 0.8 * inch
            self.height = 1.0 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            center_x = self.width / 2
            center_y = self.height / 2
            radius = 0.25 * inch
            
            # Draw background circle
            self.canv.setStrokeColor(colors.lightgrey)
            self.canv.setLineWidth(3)
            self.canv.circle(center_x, center_y, radius)
            
            # Calculate percentage
            pct = min(100, (self.value / self.max_value) * 100)
            
            # Draw filled arc (simplified - draw filled sector)
            self.canv.setFillColor(self.color)
            self.canv.setStrokeColor(self.color)
            self.canv.setLineWidth(4)
            
            # Draw arc from -90 degrees (top) clockwise
            start_angle = -90
            sweep_angle = (pct / 100) * 360
            
            # Simple approximation: draw multiple lines
            import math
            for i in range(0, int(sweep_angle), 5):
                angle = math.radians(start_angle + i)
                x1 = center_x + radius * math.cos(angle)
                y1 = center_y + radius * math.sin(angle)
                self.canv.line(center_x, center_y, x1, y1)
            
            # Draw value in center
            self.canv.setFillColor(colors.black)
            self.canv.setFont("Helvetica-Bold", 12)
            self.canv.drawCentredString(center_x, center_y - 0.05*inch, str(self.value))
            
            # Draw label
            self.canv.setFont("Helvetica", 7)
            self.canv.drawCentredString(center_x, 0.1*inch, self.label)
            
            self.canv.restoreState()
    
    gauge_table_data = [[
        CircularGauge(sample_stats['current_streak']['count'], 10, "STREAK", colors.Color(255/255, 140/255, 0/255)),
        CircularGauge(comeback_wins, 10, "COMEBACKS", colors.Color(34/255, 139/255, 34/255)),
        CircularGauge(int(scored_first_pct), 100, "SCORE 1ST %", colors.Color(30/255, 144/255, 255/255))
    ]]
    gauge_table = Table(gauge_table_data, colWidths=[0.8*inch, 0.8*inch, 0.8*inch])
    gauge_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(gauge_table)
    story.append(Spacer(1, 30))
    
    # Option 3: Horizontal Flow Diagram
    story.append(Paragraph("<b>Option 3: Horizontal Flow Diagram</b>", styles['Heading2']))
    
    class FlowSegment(Flowable):
        def __init__(self, icon, number, label, color, is_last=False):
            Flowable.__init__(self)
            self.icon = icon
            self.number = number
            self.label = label
            self.color = color
            self.is_last = is_last
            self.width = 0.7 * inch
            self.height = 1.2 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            
            # Draw connecting arrow (if not last)
            if not self.is_last:
                self.canv.setStrokeColor(self.color)
                self.canv.setLineWidth(2)
                arrow_start_x = self.width
                arrow_y = self.height / 2
                self.canv.line(arrow_start_x, arrow_y, arrow_start_x + 0.15*inch, arrow_y)
                # Arrowhead
                self.canv.line(arrow_start_x + 0.15*inch, arrow_y, arrow_start_x + 0.1*inch, arrow_y - 0.03*inch)
                self.canv.line(arrow_start_x + 0.15*inch, arrow_y, arrow_start_x + 0.1*inch, arrow_y + 0.03*inch)
            
            # Draw icon
            self.canv.setFillColor(self.color)
            self.canv.setFont("Helvetica-Bold", 24)
            icon_y = self.height - 0.3*inch
            self.canv.drawCentredString(self.width/2, icon_y, self.icon)
            
            # Draw number
            self.canv.setFont("Helvetica-Bold", 18)
            self.canv.drawCentredString(self.width/2, icon_y - 0.25*inch, str(self.number))
            
            # Draw label
            self.canv.setFont("Helvetica", 7)
            self.canv.setFillColor(colors.black)
            self.canv.drawCentredString(self.width/2, 0.15*inch, self.label)
            
            self.canv.restoreState()
    
    flow_table_data = [[
        FlowSegment("🔥", streak_text, "STREAK", colors.Color(255/255, 140/255, 0/255)),
        FlowSegment("⬆️", comeback_wins, "COMEBACKS", colors.Color(34/255, 139/255, 34/255)),
        FlowSegment("🎯", f"{scored_first_pct:.0f}%", "SCORE 1ST", colors.Color(30/255, 144/255, 255/255), is_last=True)
    ]]
    flow_table = Table(flow_table_data, colWidths=[0.85*inch, 0.85*inch, 0.85*inch])
    flow_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 30))
    
    # Option 4: Stacked Visual Bars
    story.append(Paragraph("<b>Option 4: Stacked Visual Bars</b>", styles['Heading2']))
    
    class BarMetric(Flowable):
        def __init__(self, icon, value, label, color, max_value):
            Flowable.__init__(self)
            self.icon = icon
            self.value = value
            self.label = label
            self.color = color
            self.max_value = max(max_value, value, 1)
            self.width = 1.8 * inch
            self.height = 0.35 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            
            bar_width = self.width - 0.5*inch  # Leave space for icon
            bar_height = 0.25 * inch
            bar_y = 0.05 * inch
            
            # Draw icon
            self.canv.setFillColor(self.color)
            self.canv.setFont("Helvetica-Bold", 16)
            self.canv.drawString(0.05*inch, bar_y + 0.02*inch, self.icon)
            
            # Draw bar background
            self.canv.setStrokeColor(colors.lightgrey)
            self.canv.setFillColor(colors.lightgrey)
            self.canv.setLineWidth(1)
            self.canv.rect(0.35*inch, bar_y, bar_width, bar_height, stroke=1, fill=1)
            
            # Draw filled bar
            fill_width = (self.value / self.max_value) * bar_width
            self.canv.setFillColor(self.color)
            self.canv.rect(0.35*inch, bar_y, fill_width, bar_height, stroke=0, fill=1)
            
            # Draw value on bar
            self.canv.setFillColor(colors.white)
            self.canv.setFont("Helvetica-Bold", 10)
            self.canv.drawString(0.4*inch, bar_y + 0.06*inch, str(self.value))
            
            # Draw label
            self.canv.setFillColor(colors.black)
            self.canv.setFont("Helvetica", 7)
            self.canv.drawString(0.35*inch + bar_width + 0.05*inch, bar_y + 0.08*inch, self.label)
            
            self.canv.restoreState()
    
    # Stack bars vertically
    bars_container = Table([
        [BarMetric("🔥", sample_stats['current_streak']['count'], "STREAK", colors.Color(255/255, 140/255, 0/255), 10)],
        [BarMetric("⬆️", comeback_wins, "COMEBACKS", colors.Color(34/255, 139/255, 34/255), 10)],
        [BarMetric("🎯", int(scored_first_pct), "SCORE 1ST %", colors.Color(30/255, 144/255, 255/255), 100)]
    ], colWidths=[1.8*inch], rowHeights=[0.4*inch, 0.4*inch, 0.4*inch])
    bars_container.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(bars_container)
    
    story.append(Spacer(1, 15))
    
    # Option 5: Icon + Number Display (Minimalist)
    story.append(Paragraph("<b>Option 5: Icon + Number Display (Minimalist)</b>", styles['Heading2']))
    
    class MinimalistMetric(Flowable):
        def __init__(self, icon, number, label, color):
            Flowable.__init__(self)
            self.icon = icon
            self.number = number
            self.label = label
            self.color = color
            self.width = 0.6 * inch
            self.height = 0.9 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            
            # Draw large icon
            self.canv.setFillColor(self.color)
            self.canv.setFont("Helvetica-Bold", 32)
            self.canv.drawCentredString(self.width/2, self.height - 0.35*inch, self.icon)
            
            # Draw large number
            self.canv.setFont("Helvetica-Bold", 20)
            self.canv.setFillColor(colors.black)
            self.canv.drawCentredString(self.width/2, self.height - 0.6*inch, str(self.number))
            
            # Draw subtle label
            self.canv.setFont("Helvetica", 7)
            self.canv.setFillColor(colors.grey)
            self.canv.drawCentredString(self.width/2, 0.1*inch, self.label)
            
            self.canv.restoreState()
    
    minimalist_table_data = [[
        MinimalistMetric("🔥", streak_text, "STREAK", colors.Color(255/255, 140/255, 0/255)),
        MinimalistMetric("⬆️", comeback_wins, "COMEBACKS", colors.Color(34/255, 139/255, 34/255)),
        MinimalistMetric("🎯", f"{scored_first_pct:.0f}%", "SCORE 1ST", colors.Color(30/255, 144/255, 255/255))
    ]]
    minimalist_table = Table(minimalist_table_data, colWidths=[0.7*inch, 0.7*inch, 0.7*inch])
    minimalist_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(minimalist_table)
    story.append(Spacer(1, 30))
    
    # Option 6: Combined Momentum Meter (Radial/Fan Layout)
    story.append(Paragraph("<b>Option 6: Combined Momentum Meter (Radial/Fan Layout)</b>", styles['Heading2']))
    
    class MomentumMeter(Flowable):
        def __init__(self, streak_val, comeback_val, score_first_pct):
            Flowable.__init__(self)
            self.streak_val = streak_val
            self.comeback_val = comeback_val
            self.score_first_pct = score_first_pct
            self.width = 2.5 * inch
            self.height = 2.5 * inch
            
        def wrap(self, availWidth, availHeight):
            return (self.width, self.height)
            
        def draw(self):
            self.canv.saveState()
            
            center_x = self.width / 2
            center_y = self.height / 2
            radius = 0.8 * inch
            
            # Draw three segments in a fan/radial layout
            import math
            
            # Segment 1: Streak (left)
            angle1_start = math.radians(150)
            angle1_end = math.radians(210)
            
            # Segment 2: Comebacks (top)
            angle2_start = math.radians(30)
            angle2_end = math.radians(90)
            
            # Segment 3: Score First (right)
            angle3_start = math.radians(-30)
            angle3_end = math.radians(30)
            
            # Draw arcs and labels for each segment
            colors_list = [
                colors.Color(255/255, 140/255, 0/255),  # Streak - orange
                colors.Color(34/255, 139/255, 34/255),   # Comebacks - green
                colors.Color(30/255, 144/255, 255/255)   # Score First - blue
            ]
            
            icons = ["🔥", "⬆️", "🎯"]
            labels = [f"STREAK\n{self.streak_val}", f"COMEBACKS\n{self.comeback_val}", f"SCORE 1ST\n{int(self.score_first_pct)}%"]
            values = [self.streak_val, self.comeback_val, int(self.score_first_pct)]
            
            angles = [(angle1_start, angle1_end), (angle2_start, angle2_end), (angle3_start, angle3_end)]
            
            for i, ((start_angle, end_angle), color, icon, label, value) in enumerate(zip(angles, colors_list, icons, labels, values)):
                # Draw arc
                self.canv.setStrokeColor(color)
                self.canv.setFillColor(color)
                self.canv.setLineWidth(8)
                
                # Draw filled arc segment
                mid_angle = (start_angle + end_angle) / 2
                label_radius = radius + 0.3*inch
                label_x = center_x + label_radius * math.cos(mid_angle)
                label_y = center_y + label_radius * math.sin(mid_angle)
                
                # Draw icon
                self.canv.setFont("Helvetica-Bold", 20)
                self.canv.drawCentredString(label_x, label_y + 0.15*inch, icon)
                
                # Draw value
                self.canv.setFont("Helvetica-Bold", 14)
                self.canv.setFillColor(colors.black)
                self.canv.drawCentredString(label_x, label_y - 0.05*inch, str(value))
                
                # Draw label
                self.canv.setFont("Helvetica", 7)
                self.canv.drawCentredString(label_x, label_y - 0.2*inch, label.split('\n')[0])
            
            self.canv.restoreState()
    
    momentum_meter = MomentumMeter(streak_text, comeback_wins, scored_first_pct)
    momentum_table = Table([[momentum_meter]], colWidths=[2.5*inch])
    momentum_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(momentum_table)
    
    # Build PDF
    doc.build(story)
    
    # Open in Preview
    subprocess.run(['open', '-a', 'Preview', output_file])
    print(f"Comparison PDF opened in Preview: {output_file}")
    
    return output_file

if __name__ == '__main__':
    create_comparison_pdf()

