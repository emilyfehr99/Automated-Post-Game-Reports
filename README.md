# StrideSync Dashboard

A comprehensive company website and client portal dashboard for StrideSync Hockey, featuring biomechanics analysis, performance tracking, and player management.

## Features

### Company Website
- Modern landing page with hero section
- Services showcase with individual service pages
- About Us section
- Testimonials
- Contact form
- Careers page
- Resources page

### Client Portal Dashboard
- **Player Profile**: View player stats, team info, and session status
- **Biomechanics Analysis**: Interactive radar chart showing key biomechanical metrics
- **Quick Stats**: Overview of recent performance metrics
- **Player Wellness Survey**: Track sleep quality, energy levels, and recovery
- **Performance Alerts**: Important notifications about performance metrics
- **Session History**: View past training sessions with details
- **Injury Prediction**: Risk assessment based on biomechanics data
- **Skeleton Overlay Analysis**: Before/after skeleton video comparison with movement selector
- **Resources Page**: Training guides, video library, and tools
- **About Us Page**: Company information and location

## Setup

1. Install dependencies:
```bash
pip install flask flask-socketio
```

2. Add your logo file:
   - Place `logo.png` in the `static/` directory
   - The logo is currently ignored by `.gitignore` (add with `git add -f static/logo.png` if needed)

3. Run the application:
```bash
python3 company_website.py
```

4. Access the website:
   - Company website: http://localhost:5001
   - Client portal login: http://localhost:5001/login
   - Default credentials: `alexander@stridesync.com` / `password123`

## Project Structure

```
├── company_website.py          # Main Flask application
├── templates/
│   ├── company_index.html      # Company landing page
│   ├── login.html              # Client portal login
│   ├── original_client_portal.html  # Main client dashboard
│   ├── client_about.html       # Client portal About page
│   ├── service_page.html       # Individual service pages
│   ├── careers.html            # Careers page
│   ├── resources.html          # Resources page
│   └── contact_success.html    # Contact form success page
├── static/
│   ├── company_style.css       # Company website styles
│   ├── company_script.js       # Company website JavaScript
│   ├── client_portal_styles.css # Client portal styles
│   ├── client_portal_script.js  # Client portal JavaScript
│   └── logo.png                # Company logo (add manually)
└── README.md                   # This file
```

## Color Scheme

- Primary Blue: `#2563eb`
- Dark Blue: `#1e40af`
- White: `#ffffff`
- Gray: `#6b7280`
- Green: `#10b981`

## Technologies Used

- Flask (Python web framework)
- Bootstrap 5
- Chart.js (for biomechanics radar chart)
- Font Awesome (icons)
- HTML5/CSS3/JavaScript

## Notes

- The client portal uses session-based authentication
- The dashboard is designed for a specific client (Alexander Andre) but can be customized
- All styling follows a consistent blue/white theme
- The sidebar menu opens from the right side
- Performance data is currently static but can be connected to a backend API
