from PIL import Image, ImageChops
import os

bg_path = "/Users/emilyfehr8/CascadeProjects/automated-post-game-reports/assets/Paper.png"
if os.path.exists(bg_path):
    img = Image.open(bg_path)
    gray = img.convert('L')
    extrema = gray.getextrema()
    print(f"Paper.png min/max grayscale: {extrema}")
else:
    print("Paper.png not found")
