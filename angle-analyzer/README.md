# Angle Analyzer v2.0

A comprehensive web application for measuring angles in both images and videos with advanced drawing capabilities. Perfect for analyzing hockey plays, architectural drawings, or any visual angle measurements.

## Features

### Image Analysis Tab
- **Image Upload**: Upload any image file (PNG, JPG, GIF, etc.)
- **Interactive Measurement**: Click two points to measure the angle of the line
- **Real-time Calculation**: Instant angle calculation with precision to 2 decimal places
- **Visual Feedback**: Points are numbered and lines are drawn to show the measured angle
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Keyboard Shortcuts**: Press 'R' or 'Escape' to reset
- **Modern UI**: Cyberpunk-inspired design with smooth animations

### Video Analysis Tab (NEW!)
- **Video Upload**: Upload video files (MP4, WebM, OGG)
- **Video Playback Controls:**
  - Play/Pause with spacebar or button
  - Step forward/backward frame by frame
  - Speed control (0.1x to 3.0x)
  - Clear all drawings
- **Drawing Tools:**
  - 📏 **Line Tool**: Draw straight lines between two points
  - 📐 **Angle Tool**: Measure and display angles with visual arcs
  - ✏️ **Freehand Tool**: Draw freehand annotations
  - 🧹 **Eraser Tool**: Remove drawings (coming soon)
  - Color picker for custom drawing colors
- **Canvas Overlay**: Draw directly on video frames
- **Frame Counter**: Real-time frame information display

## Quick Start

### Option 1: Direct File Opening
Simply open `index.html` in your web browser:
```bash
open index.html
```

### Option 2: Local Web Server
For better performance and to avoid CORS issues:

#### Using Python (recommended):
```bash
cd angle-analyzer
python -m http.server 8000
```
Then open http://localhost:8000 in your browser.

#### Using Node.js:
```bash
cd angle-analyzer
npx http-server
```

#### Using PHP:
```bash
cd angle-analyzer
php -S localhost:8000
```

## How to Use

### Image Analysis Tab
1. **Upload Image**: Click "Choose Image" and select an image file
2. **Measure Angle**: Click two points on the image:
   - First click: Start point of the line
   - Second click: End point of the line
3. **View Result**: The angle will be displayed in degrees relative to horizontal (0°)
4. **Reset**: Click "Reset" or press 'R' to start a new measurement

### Video Analysis Tab
1. **Upload Video**: Click "Choose Video" and select a video file
2. **Control Playback**: Use the video controls to navigate through the video
3. **Select Drawing Tool**: Choose from Line, Angle, Freehand, or Eraser tools
4. **Draw on Video**: Click and drag to draw annotations on the video frame
5. **Adjust Speed**: Use the speed slider to slow down or speed up playback
6. **Step Through Frames**: Use step forward/backward for precise analysis
7. **Clear Drawings**: Click "Clear Drawings" to remove all annotations

## File Structure

```
angle-analyzer/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── requirements.txt    # Dependencies (none required)
└── README.md          # This file
```

## Technical Details

- **Pure Frontend**: No server-side dependencies required
- **Canvas API**: Uses HTML5 Canvas for image rendering and drawing
- **Vector Math**: Implements dot product calculation for angle measurement
- **Responsive**: CSS Grid and Flexbox for responsive design
- **Modern JavaScript**: ES6+ features with class-based architecture

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Keyboard Shortcuts

- `R` - Reset current measurement (Image tab) or clear drawings (Video tab)
- `Escape` - Reset current measurement (Image tab) or clear drawings (Video tab)
- `Spacebar` - Play/Pause video (Video tab only)

## Features in Detail

### Angle Calculation
The app uses vector mathematics to calculate angles:
1. Creates vectors from the vertex to each endpoint
2. Calculates the dot product of the vectors
3. Uses the arccosine function to determine the angle
4. Converts from radians to degrees

### Visual Enhancements
- Numbered points for easy identification
- Colored lines showing the measured angle
- Arc indicator at the vertex
- Smooth animations and hover effects
- Loading indicators for image processing

### Responsive Design
- Adapts to different screen sizes
- Touch-friendly interface for mobile devices
- Optimized canvas sizing for various viewports

## Troubleshooting

### Image Not Loading
- Ensure the image file is a supported format (PNG, JPG, GIF, WebP)
- Check that the file isn't corrupted
- Try a different image file

### Canvas Not Responding
- Refresh the page
- Check browser console for JavaScript errors
- Ensure JavaScript is enabled in your browser

### Angle Calculation Issues
- Make sure you click exactly 3 points
- Points should be distinct (not overlapping)
- The vertex (middle point) should be the corner of the angle you want to measure

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## Version History

- **v2.0** - Major update with video analysis capabilities
  - Added tabbed interface for Image and Video analysis
  - Video playback controls (play/pause, speed control, frame stepping)
  - Drawing tools (line, angle, freehand, eraser)
  - Canvas overlay for drawing on video frames
  - Color picker for custom drawing colors
  - Frame counter and video information display
- **v1.0** - Initial release with basic angle measurement functionality
