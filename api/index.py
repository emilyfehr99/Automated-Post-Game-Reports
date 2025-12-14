from api_server import app

# Vercel serverless handler
# This wraps the Flask app for Vercel's Python runtime
handler = app
