"""
Hudl Instat Credentials
Add your authorized Hudl credentials here
"""

# Hudl Instat Login Credentials (Shared Account)
HUDL_USERNAME = "your_username_here"  # Replace with your actual username
HUDL_PASSWORD = "your_password_here"  # Replace with your actual password

# Multi-User Configuration
MAX_CONCURRENT_SESSIONS = 3  # Maximum number of users that can be logged in simultaneously
SESSION_TIMEOUT_MINUTES = 30  # How long a session stays active (in minutes)

# User Identifiers (for tracking who is using the API)
# Add your team members here
TEAM_MEMBERS = {
    "emily": "Emily Fehr",
    "coach1": "Head Coach",
    "analyst1": "Data Analyst",
    "assistant1": "Assistant Coach"
}

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8001
DEBUG = True
