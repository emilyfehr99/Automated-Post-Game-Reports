#!/usr/bin/env python3

import json
import os
from src.process_clip import create_html_visualization

# Load the existing JSON data
json_path = "test_fast_500/player_detection_data_20250818_143440.json"
with open(json_path, 'r') as f:
    processed_frames_info = json.load(f)

# Set up paths
output_dir = "test_fast_500"
rink_image_path = "output/tracking_results_20250817_210815/rink_resized.png"
fps = 30  # Default FPS

# Generate visualization
create_html_visualization(processed_frames_info, output_dir, rink_image_path, fps)

print(f"Visualization created in {output_dir}/visualization.html")
