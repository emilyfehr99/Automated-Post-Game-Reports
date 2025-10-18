#!/usr/bin/env python3
"""
Audio to Text Converter Web Interface
A Flask web application for uploading MP4/MPV files and downloading transcriptions.
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import shutil
from audio_to_text_converter import AudioToTextConverter

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'mpv', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'wav', 'mp3', 'm4a', 'flac', 'ogg'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global converter instance
converter = None
processing_jobs = {}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_converter():
    """Initialize the audio converter."""
    global converter
    if converter is None:
        print("Initializing Whisper model...")
        converter = AudioToTextConverter(model_size="base")
        print("Model ready!")

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start processing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    # Get processing options
    model_size = request.form.get('model', 'base')
    language = request.form.get('language', 'auto')
    include_timestamps = request.form.get('timestamps') == 'true'
    include_speakers = request.form.get('speakers') == 'true'
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    # Generate job ID
    job_id = f"job_{timestamp}_{int(time.time())}"
    
    # Start processing in background
    thread = threading.Thread(
        target=process_file_background,
        args=(job_id, filepath, filename, model_size, language, include_timestamps, include_speakers)
    )
    thread.daemon = True
    thread.start()
    
    # Store job info
    processing_jobs[job_id] = {
        'status': 'processing',
        'filename': filename,
        'start_time': datetime.now().isoformat(),
        'progress': 0
    }
    
    return jsonify({
        'job_id': job_id,
        'message': 'File uploaded and processing started'
    })

def process_file_background(job_id, filepath, original_filename, model_size, language, include_timestamps, include_speakers):
    """Process file in background thread."""
    try:
        # Update progress
        processing_jobs[job_id]['progress'] = 10
        processing_jobs[job_id]['status'] = 'loading_model'
        
        # Initialize converter with specified model
        global converter
        if converter is None or converter.model_size != model_size:
            converter = AudioToTextConverter(model_size=model_size)
        
        processing_jobs[job_id]['progress'] = 30
        processing_jobs[job_id]['status'] = 'extracting_audio'
        
        # Process file
        output_filename = f"{Path(original_filename).stem}_transcript.txt"
        output_path = os.path.join(OUTPUT_FOLDER, f"{job_id}_{output_filename}")
        
        processing_jobs[job_id]['progress'] = 50
        processing_jobs[job_id]['status'] = 'transcribing'
        
        # Set language
        lang = None if language == 'auto' else language
        
        # Convert file
        success = converter.process_file(
            filepath,
            output_path,
            lang,
            include_timestamps,
            include_speakers
        )
        
        if success:
            processing_jobs[job_id]['progress'] = 100
            processing_jobs[job_id]['status'] = 'completed'
            processing_jobs[job_id]['output_file'] = output_path
            processing_jobs[job_id]['output_filename'] = output_filename
        else:
            processing_jobs[job_id]['status'] = 'failed'
            processing_jobs[job_id]['error'] = 'Transcription failed'
    
    except Exception as e:
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['error'] = str(e)
    
    finally:
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get processing status for a job."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_jobs[job_id])

@app.route('/download/<job_id>')
def download_file(job_id):
    """Download the transcription file."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    output_path = job['output_file']
    output_filename = job['output_filename']
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'Output file not found'}), 404
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_filename,
        mimetype='text/plain'
    )

@app.route('/download_pdf/<job_id>')
def download_pdf(job_id):
    """Download the transcription as PDF."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    output_path = job['output_file']
    output_filename = job['output_filename'].replace('.txt', '.pdf')
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'Output file not found'}), 404
    
    # Convert to PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Create PDF
        pdf_path = output_path.replace('.txt', '.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom style for transcript
        transcript_style = ParagraphStyle(
            'Transcript',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=0,
            rightIndent=0
        )
        
        # Read text file
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into paragraphs
        paragraphs = content.split('\n')
        story = []
        
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para, transcript_style))
                story.append(Spacer(1, 6))
        
        doc.build(story)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
    
    except ImportError:
        return jsonify({'error': 'PDF generation requires reportlab. Install with: pip install reportlab'}), 500
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@app.route('/jobs')
def list_jobs():
    """List all processing jobs."""
    return jsonify(processing_jobs)

@app.route('/cleanup')
def cleanup():
    """Clean up old files and jobs."""
    current_time = time.time()
    cutoff_time = current_time - (24 * 60 * 60)  # 24 hours ago
    
    # Clean up old jobs
    jobs_to_remove = []
    for job_id, job in processing_jobs.items():
        try:
            job_time = datetime.fromisoformat(job['start_time']).timestamp()
            if job_time < cutoff_time:
                jobs_to_remove.append(job_id)
                # Remove output file
                if 'output_file' in job and os.path.exists(job['output_file']):
                    os.remove(job['output_file'])
        except:
            pass
    
    for job_id in jobs_to_remove:
        del processing_jobs[job_id]
    
    return jsonify({'cleaned': len(jobs_to_remove)})

if __name__ == '__main__':
    # Initialize converter on startup
    init_converter()
    
    print("Starting Audio to Text Converter Web Interface...")
    print("Open your browser and go to: http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
