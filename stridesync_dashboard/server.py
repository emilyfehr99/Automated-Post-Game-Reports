#!/usr/bin/env python3
"""
Simple HTTP server for StrideSync Hockey Dashboard
Run this file to serve the dashboard locally
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Server configuration
    PORT = 8000
    HOST = 'localhost'
    
    # Create server
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 StrideSync Hockey Dashboard Server")
        print(f"📍 Serving at: http://{HOST}:{PORT}")
        print(f"📁 Directory: {script_dir}")
        print(f"🔗 Open your browser and go to: http://{HOST}:{PORT}")
        print(f"⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://{HOST}:{PORT}')
            print("🌐 Browser opened automatically")
        except:
            print("⚠️  Could not open browser automatically")
        
        print("-" * 50)
        
        # Start the server
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    main()






















