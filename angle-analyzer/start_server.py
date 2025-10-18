#!/usr/bin/env python3
"""
Angle Analyzer v1.0 - Simple HTTP Server Launcher
This script starts a local web server to serve the Angle Analyzer application.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_server(port=8000):
    """Start the HTTP server and open the application in the browser."""
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create a simple HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 Angle Analyzer v1.0 Server Starting...")
            print(f"📡 Server running at: http://localhost:{port}")
            print(f"📁 Serving files from: {script_dir}")
            print(f"🌐 Opening browser...")
            print(f"⏹️  Press Ctrl+C to stop the server")
            print("-" * 50)
            
            # Open the browser
            webbrowser.open(f'http://localhost:{port}')
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8000.")
    
    start_server(port)
