#!/usr/bin/env python3
"""
Company Website with Client Portal
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Simple user database (in production, use a real database)
USERS = {
    'client1@example.com': {'password': 'password123', 'name': 'Alexander Andre', 'role': 'client'},
    'admin@example.com': {'password': 'admin123', 'name': 'Admin User', 'role': 'admin'},
}

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Landing/About page"""
    return render_template('company_index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in USERS and USERS[email]['password'] == password:
            session['user_email'] = email
            session['user_name'] = USERS[email]['name']
            session['user_role'] = USERS[email]['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Client dashboard"""
    user_name = session.get('user_name', 'User')
    return render_template('client_dashboard.html', user_name=user_name)

@app.route('/service/<service_name>')
def service(service_name):
    """Individual service pages"""
    service_data = {
        'remote-training': {
            'title': 'Remote Training',
            'icon': '💻',
            'description': 'Professional biomechanical analysis and training programs delivered remotely. Get expert coaching from anywhere in the world.',
            'features': [
                'Virtual consultations and assessments',
                'Remote video analysis',
                'Online training program delivery',
                'Real-time feedback and coaching',
                'Flexible scheduling',
                'Access to expert coaches worldwide'
            ],
            'benefits': [
                'Train from anywhere, anytime',
                'Access to top-tier coaching',
                'Flexible scheduling',
                'Cost-effective training solutions',
                'Personalized programs delivered digitally'
            ]
        },
        'performance-tracking': {
            'title': 'Performance Tracking',
            'icon': '📊',
            'description': 'Real-time performance metrics and progress tracking with precision analytics.',
            'features': [
                'Speed and acceleration tracking',
                'Agility metrics monitoring',
                'Power output measurement',
                'Recovery status tracking',
                'Progress dashboards',
                'Historical trend analysis'
            ],
            'benefits': [
                'Track improvement over time',
                'Identify performance trends',
                'Data-driven training adjustments',
                'Motivation through visible progress',
                'Comprehensive performance insights'
            ]
        },
        'assessments': {
            'title': 'Assessments',
            'icon': '🔍',
            'description': 'Comprehensive biomechanical and performance assessments with detailed analysis.',
            'features': [
                'Full biomechanical scan',
                'Movement pattern analysis',
                'Performance evaluation',
                'Injury risk assessment',
                'Detailed reporting',
                'Personalized recommendations'
            ],
            'benefits': [
                'Complete performance picture',
                'Identify strengths and weaknesses',
                'Baseline for future comparisons',
                'Injury prevention insights',
                'Customized training recommendations'
            ]
        }
    }
    
    if service_name not in service_data:
        return redirect(url_for('index'))
    
    return render_template('service_page.html', service=service_data[service_name], service_name=service_name)

@app.route('/careers')
def careers():
    """Careers page"""
    return render_template('careers.html')

@app.route('/resources')
def resources():
    """Resources page"""
    return render_template('resources.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form handler"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        message = request.form.get('message')
        
        # In production, send email or save to database
        print(f"Contact form submission: {name} ({email}) - {message}")
        
        # Return success message
        return render_template('contact_success.html', name=name)
    
    return redirect(url_for('index') + '#contact')

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """API endpoint for dashboard data"""
    # In production, fetch real data from database
    return jsonify({
        'last_session': 'March 15, 2024',
        'next_session': 'March 18, 2024',
        'last_session_status': 'Completed',
        'next_session_status': 'Scheduled',
        'goals': 2,
        'assists': 22,
        'points': 24,
        'toi': '18:34',
        'biomechanics': {
            'knee_flexion': 85,
            'hip_extension': 72,
            'ankle_dorsiflexion': 68,
            'stance_width': 24
        },
        'performance_trends': {
            'speed': {'change': 8, 'positive': True},
            'agility': {'change': 12, 'positive': True},
            'recovery': {'change': -3, 'positive': False}
        },
        'quick_stats': {
            'last_session_score': 92,
            'max_score': 100,
            'sessions_this_week': 3,
            'goal_progress': 78
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    print("🌐 Starting Company Website...")
    print(f"📊 Access at: http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)

