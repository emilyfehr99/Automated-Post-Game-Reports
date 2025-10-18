# Hockey Practice Pro

A professional hockey practice planning and drill management platform designed for coaches at all levels. Create, manage, and share practice plans with advanced drill drawing tools and comprehensive team management features.

## Features

### 🏒 Drill Drawing Tool
- Interactive hockey rink canvas
- Add players, pucks, and movement arrows
- Custom drill creation with descriptions
- Save and export drill designs

### 📋 Practice Plan Builder
- Create structured practice sessions
- Add drills from library or custom creations
- Set drill durations and categories
- Practice plan summary and statistics

### 📚 Drill Library
- Browse and search existing drills
- Categorize drills by type (Offensive, Defensive, Systems, etc.)
- Add custom drills to the library
- Quick drill preview and selection

### 🎯 Practice Management
- Store practice plans indefinitely
- Edit and modify existing plans
- Share plans digitally or print
- Team management and collaboration

### 👤 User Management
- Secure user authentication
- Personal drill libraries
- User-specific practice plans
- Cross-device synchronization

### 💳 Subscription Features
- Free tier with basic features
- Pro tier with unlimited drills and plans
- Team collaboration features
- Priority support

## Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS with custom hockey theme
- **Animations**: Framer Motion
- **Canvas**: Fabric.js for drill drawing
- **Icons**: Lucide React
- **Fonts**: Russo One (headings), Courier New (body text)

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd hockey-practice-planner
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
hockey-practice-planner/
├── app/
│   ├── globals.css          # Global styles and hockey theme
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main application page
├── components/
│   ├── DrillDrawingTool.tsx # Interactive drill creation tool
│   └── PracticePlanBuilder.tsx # Practice plan creation interface
├── public/                  # Static assets
└── ...config files
```

## Key Components

### Drill Drawing Tool
- **Canvas**: Interactive hockey rink with Fabric.js
- **Tools**: Player placement, puck positioning, movement arrows
- **Features**: Save/load drill designs, export functionality

### Practice Plan Builder
- **Drill Library**: Browse and select from existing drills
- **Plan Structure**: Organize drills with timing and descriptions
- **Summary**: Automatic calculation of total time and drill statistics

## Customization

### Theme Colors
The application uses a custom hockey-themed color palette:
- Hockey Blue: `#003366`
- Hockey Red: `#CC0000` 
- Hockey Gold: `#FFD700`
- Ice Blue: `#E6F3FF`

### Fonts
- **Headings**: Russo One (hockey-style font)
- **Body Text**: Courier New (as per user preference)

## Features in Development

- [ ] Team roster management
- [ ] Video integration for drills
- [ ] PDF export functionality
- [ ] Social sharing capabilities
- [ ] Mobile responsive design
- [ ] User authentication
- [ ] Cloud storage integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Please respect the original Ice Hockey Systems platform and its intellectual property.

## Acknowledgments

Inspired by Ice Hockey Systems (IHS) - a comprehensive platform for hockey coaches worldwide.
