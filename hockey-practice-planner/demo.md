# Hockey Practice Planner - Demo Guide

## Quick Start

1. **Setup the application:**
   ```bash
   ./setup.sh
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Demo Features

### 1. Dashboard
- View quick statistics and recent practice plans
- Quick access to create new content
- Overview of your hockey coaching tools

### 2. Drill Library
- Browse existing drills with previews
- Search and filter drills by category
- Add new drills to your library

### 3. Practice Plans
- Create structured practice sessions
- Add drills from your library
- Set drill durations and descriptions
- View practice summaries

### 4. Create New Content

#### Practice Plan Builder
1. Click "Create" tab
2. Click "Practice Plan" card
3. Enter practice plan name and description
4. Click "Add Drill" to browse drill library
5. Select drills and set durations
6. Save your practice plan

#### Drill Drawing Tool
1. Click "Create" tab
2. Click "Custom Drill" card
3. Use the drawing tools:
   - **Select**: Move and edit objects
   - **Player**: Add players to the rink
   - **Puck**: Place pucks on the ice
   - **Arrow**: Add movement directions
4. Enter drill name and description
5. Save your custom drill

### 5. Hockey Rink Canvas
The drill drawing tool features:
- **Rink Outline**: Standard hockey rink dimensions
- **Center Line**: Divides offensive and defensive zones
- **Face-off Circles**: For positioning reference
- **Goal Areas**: Both ends of the rink
- **Interactive Tools**: Click to add players, pucks, and arrows

## Sample Workflow

### Creating a Power Play Practice

1. **Start a new practice plan:**
   - Go to "Create" → "Practice Plan"
   - Name: "Power Play Practice"
   - Description: "Focus on power play setup and execution"

2. **Add warm-up drill:**
   - Click "Add Drill"
   - Select "Warm-up Skating" (10 minutes)

3. **Add power play drill:**
   - Click "Add Drill" 
   - Select "Power Play Setup" (20 minutes)

4. **Add shooting practice:**
   - Click "Add Drill"
   - Select "Shooting Practice" (15 minutes)

5. **Add cool-down:**
   - Click "Add Drill"
   - Select "Cool Down" (10 minutes)

6. **Review and save:**
   - Check total time: 55 minutes
   - Review drill sequence
   - Click "Save"

### Creating a Custom Drill

1. **Open drill drawing tool:**
   - Go to "Create" → "Custom Drill"

2. **Design the drill:**
   - Use "Player" tool to place players
   - Use "Puck" tool to show puck position
   - Use "Arrow" tool to show movement
   - Add drill name: "2-on-1 Breakout"
   - Add description: "Practice 2-on-1 situations from defensive zone"

3. **Save the drill:**
   - Click "Save Drill"
   - Drill is added to your library

## Processing Your PDF Drills

If you have the `ihs-print-1757448115819.pdf` file:

1. **Install Python dependencies:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

2. **Process the PDF:**
   ```bash
   python process-drill-pdf.py
   ```

3. **Drills will be extracted to:**
   - `public/drills/` - Individual drill images
   - `public/drills/metadata.json` - Drill information

## Tips for Best Results

### Practice Planning
- Start with warm-up drills (5-10 minutes)
- Include skill development (15-20 minutes)
- Add system work (15-25 minutes)
- End with cool-down (5-10 minutes)
- Total practice: 45-75 minutes

### Drill Creation
- Use clear, simple diagrams
- Show player positions clearly
- Include movement arrows
- Add descriptive names
- Categorize drills properly

### Organization
- Use consistent naming conventions
- Add detailed descriptions
- Categorize drills by skill level
- Keep practice plans focused

## Troubleshooting

### Common Issues

1. **Canvas not loading:**
   - Check browser console for errors
   - Ensure Fabric.js is loaded properly

2. **Drills not saving:**
   - Check that drill name is entered
   - Verify all required fields are filled

3. **PDF processing fails:**
   - Ensure PDF file exists in parent directory
   - Check Python dependencies are installed
   - Verify file permissions

### Getting Help

- Check the browser console for error messages
- Review the README.md for detailed setup instructions
- Ensure all dependencies are properly installed

## Next Steps

- Customize the color scheme to match your team
- Add your team logo to practice plans
- Create drill categories specific to your coaching style
- Export practice plans as PDFs for printing
- Share practice plans with assistant coaches
