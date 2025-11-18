# Company Website with Client Portal

A modern, professional website with client portal login functionality, styled to match the StrideSync Hockey theme (blue and white color scheme).

## Features

- **Landing/About Page**: Company information, mission, principles, and location
- **Client Portal Login**: Secure login system for clients
- **Client Dashboard**: Personalized dashboard with:
  - Player profile and statistics
  - Biomechanics analysis with radar chart
  - Performance trends
  - Quick stats
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design matching the StrideSync theme

## File Structure

```
CascadeProjects/
├── company_website.py          # Main Flask application
├── templates/
│   ├── company_index.html      # Landing/About page
│   ├── login.html              # Login page
│   └── client_dashboard.html   # Client dashboard
└── static/
    ├── company_style.css        # Styling (blue/white theme)
    └── company_script.js        # JavaScript functionality
```

## Setup Instructions

1. **Install Dependencies** (if not already installed):
   ```bash
   pip install flask
   ```

2. **Set Secret Key** (for production):
   ```bash
   export SECRET_KEY='your-secret-key-here'
   ```
   Or modify `company_website.py` to use a secure secret key.

3. **Run the Application**:
   ```bash
   python company_website.py
   ```

4. **Access the Website**:
   - Landing page: http://localhost:5000/
   - Login page: http://localhost:5000/login
   - Dashboard: http://localhost:5000/dashboard (requires login)

## Demo Credentials

- **Email**: `client1@example.com`
- **Password**: `password123`

## Customization

### Adding Users

Edit the `USERS` dictionary in `company_website.py`:

```python
USERS = {
    'client1@example.com': {
        'password': 'password123',
        'name': 'Alexander Andre',
        'role': 'client'
    },
    # Add more users...
}
```

### Changing Company Information

Edit the HTML templates:
- `templates/company_index.html` - Landing page content
- `templates/client_dashboard.html` - Dashboard content

### Styling

Modify `static/company_style.css` to change colors, fonts, or layout. The theme uses:
- Primary Blue: `#2563eb`
- Dark Blue: `#1e40af`
- White: `#ffffff`
- Light Gray: `#f3f4f6`

### Dashboard Data

Modify the `/api/dashboard-data` endpoint in `company_website.py` to fetch real data from your database.

## Production Deployment

For production use:

1. **Use a Real Database**: Replace the simple `USERS` dictionary with a database (SQLite, PostgreSQL, etc.)

2. **Secure Secret Key**: Use a strong, random secret key:
   ```python
   import secrets
   app.secret_key = secrets.token_hex(32)
   ```

3. **Password Hashing**: Use proper password hashing (e.g., `werkzeug.security.check_password_hash`)

4. **HTTPS**: Deploy with HTTPS enabled

5. **Environment Variables**: Use environment variables for sensitive configuration

## Integration with Existing Dashboard

If you want to integrate this with your existing `prediction_dashboard.py`, you can:

1. Merge the routes into one Flask app
2. Share authentication between both dashboards
3. Use the same user system for both

## Support

For questions or issues, refer to the Flask documentation: https://flask.palletsprojects.com/

