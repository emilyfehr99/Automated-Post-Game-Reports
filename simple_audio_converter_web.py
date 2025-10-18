#!/usr/bin/env python3
"""
Simple Audio to Text Converter Web Interface
A simplified version that works with audio files directly (no video processing for now)
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import whisper
import librosa
import soundfile as sf
import numpy as np
import subprocess
import shutil
# from transformers import pipeline  # Temporarily disabled due to mutex issues

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'mp4'}  # Simplified for now
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global converter instance
model = None
# summarizer = None  # Temporarily disabled
processing_jobs = {}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_model():
    """Initialize the Whisper model."""
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Whisper model loaded successfully!")
    
    # AI summarizer temporarily disabled due to mutex issues
    # if summarizer is None:
    #     print("Loading AI summarizer...")
    #     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    #     print("AI summarizer loaded successfully!")

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
        return jsonify({'error': 'File type not supported. Please use: WAV, MP3, M4A, FLAC, OGG, or MP4'}), 400
    
    # Get processing options (always use best settings)
    model_size = 'large'  # Always use large model for maximum accuracy
    language = 'en'  # Always use English
    include_timestamps = True  # Always include timestamps
    include_speakers = request.form.get('speakers') == 'true'
    # include_takeaways = request.form.get('takeaways') == 'true'  # Removed
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    
    # Generate job ID
    job_id = f"job_{timestamp}_{int(time.time())}"
    
    # Store job info FIRST
    processing_jobs[job_id] = {
        'status': 'processing',
        'filename': filename,
        'start_time': datetime.now().isoformat(),
        'progress': 0
    }
    
    # Start processing in background
    print(f"Starting background processing for job {job_id}")
    thread = threading.Thread(
        target=process_file_background,
        args=(job_id, filepath, filename, model_size, language, include_timestamps, include_speakers)
    )
    thread.daemon = True
    thread.start()
    print(f"Background thread started for job {job_id}")
    
    # Small delay to ensure job is stored
    time.sleep(0.1)
    
    return jsonify({
        'job_id': job_id,
        'message': 'File uploaded and processing started'
    })

def process_file_background(job_id, filepath, original_filename, model_size, language, include_timestamps, include_speakers):
    """Process file in background thread."""
    print(f"Background processing started for job {job_id}")
    try:
        # Ensure job exists in processing_jobs
        if job_id not in processing_jobs:
            print(f"Job {job_id} not found in processing_jobs")
            return
            
        print(f"Updating progress for job {job_id}")
        # Update progress
        processing_jobs[job_id]['progress'] = 10
        processing_jobs[job_id]['status'] = 'loading_model'
        
        # Initialize model if needed (use base model for speed)
        global model
        if model is None:
            # Use base model for much faster processing
            model = whisper.load_model("base")
        # summarizer temporarily disabled
        
        # Check if it's a video file and extract audio
        file_extension = Path(filepath).suffix.lower()
        if file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            processing_jobs[job_id]['status'] = 'extracting_audio'
            processing_jobs[job_id]['progress'] = 30
            print(f"Extracting audio from video file: {filepath}")
            preprocessed_path = extract_audio_from_video(filepath)
        else:
            preprocessed_path = filepath  # Use original file directly
        
        processing_jobs[job_id]['status'] = 'transcribing'
        processing_jobs[job_id]['progress'] = 50
        
        # Set language
        lang = None if language == 'auto' else language
        
        # Transcribe audio with optimized settings for speed
        result = model.transcribe(
            preprocessed_path,
            language=lang,
            word_timestamps=True,
            verbose=False,
            temperature=0.0,  # More deterministic output
            beam_size=1,      # Faster processing
            best_of=1,        # Single attempt for speed
            patience=0.0,     # No patience for speed
            length_penalty=1.0,
            suppress_tokens=[-1]  # Suppress special tokens
        )
        
        processing_jobs[job_id]['progress'] = 80
        processing_jobs[job_id]['status'] = 'formatting'
        
        # Format output
        output_filename = f"{Path(original_filename).stem}_transcript.txt"
        output_path = os.path.join(OUTPUT_FOLDER, f"{job_id}_{output_filename}")
        
        # Create formatted text
        formatted_text = format_transcription(result, include_timestamps, include_speakers)
        
        # Save file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        # Extract unique speakers
        speakers = set()
        if result.get("segments"):
            for segment in result["segments"]:
                if "speaker" in segment:
                    speakers.add(segment["speaker"])
        
        processing_jobs[job_id]['progress'] = 100
        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['output_file'] = output_path
        processing_jobs[job_id]['output_filename'] = output_filename
        processing_jobs[job_id]['speakers'] = sorted(list(speakers))
        
        # Clean up temporary files
        try:
            if preprocessed_path != filepath and os.path.exists(preprocessed_path):
                os.remove(preprocessed_path)
                print(f"Cleaned up temporary file: {preprocessed_path}")
        except Exception as e:
            print(f"Failed to clean up temporary file: {e}")
    
    except Exception as e:
        if job_id in processing_jobs:
            processing_jobs[job_id]['status'] = 'failed'
            processing_jobs[job_id]['error'] = str(e)
        print(f"Error processing job {job_id}: {e}")
    
    finally:
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass

def format_transcription(result, include_timestamps=True, include_speakers=False):
    """Format transcription result into readable text."""
    if not result:
        return "Transcription failed."
    
    formatted_text = []
    
    # Add header
    formatted_text.append("=" * 60)
    formatted_text.append("MEETING TRANSCRIPTION")
    formatted_text.append("=" * 60)
    formatted_text.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    formatted_text.append(f"Model: Whisper base")
    formatted_text.append("")
    
    # Add timestamped version only
    if include_timestamps and "segments" in result:
        formatted_text.append("TRANSCRIPT WITH TIMESTAMPS:")
        formatted_text.append("-" * 40)
        
        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            if include_speakers and "speaker" in segment:
                formatted_text.append(f"[{start_time} - {end_time}] Speaker {segment['speaker']}: {text}")
            else:
                formatted_text.append(f"[{start_time} - {end_time}] {text}")
    
    return "\n".join(formatted_text)

def format_timestamp(seconds):
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def preprocess_audio(audio_path):
    """Preprocess audio for better transcription accuracy."""
    try:
        # Load audio with librosa for better quality
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        # Normalize audio
        audio = librosa.util.normalize(audio)
        
        # Apply noise reduction (simple spectral gating)
        audio = reduce_noise(audio, sr)
        
        # Save preprocessed audio with proper format
        preprocessed_path = audio_path.replace('.', '_preprocessed.')
        # Ensure we use a supported format
        if preprocessed_path.endswith('.m4a'):
            preprocessed_path = preprocessed_path.replace('.m4a', '.wav')
        
        sf.write(preprocessed_path, audio, sr, format='WAV')
        
        return preprocessed_path
    except Exception as e:
        print(f"Audio preprocessing failed: {e}")
        return audio_path  # Return original if preprocessing fails

def reduce_noise(audio, sr, noise_reduction_factor=0.1):
    """Simple noise reduction using spectral gating."""
    try:
        # Compute STFT
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise floor (using first 10% of audio)
        noise_frames = int(0.1 * magnitude.shape[1])
        noise_floor = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Apply spectral gating
        gate = magnitude > (noise_floor * (1 + noise_reduction_factor))
        magnitude_clean = magnitude * gate
        
        # Reconstruct audio
        stft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(stft_clean)
        
        return audio_clean
    except Exception as e:
        print(f"Noise reduction failed: {e}")
        return audio

def extract_audio_from_video(video_path):
    """Extract audio from video file using ffmpeg."""
    try:
        # Check if ffmpeg is available
        ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
        if not os.path.exists(ffmpeg_path):
            print("ffmpeg not found, trying to process video directly")
            return video_path
        
        # Create output audio file path
        audio_path = video_path.rsplit('.', 1)[0] + '_extracted.wav'
        
        # Extract audio using ffmpeg with full path
        ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
        cmd = [
            ffmpeg_path, '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # Audio codec
            '-ar', '16000',  # Sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Audio extracted successfully: {audio_path}")
            return audio_path
        else:
            print(f"ffmpeg failed: {result.stderr}")
            return video_path
            
    except Exception as e:
        print(f"Audio extraction failed: {e}")
        return video_path

@app.route('/status/<job_id>')
def get_status(job_id):
    """Get processing status for a job."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_jobs[job_id])

@app.route('/update_speakers/<job_id>', methods=['POST'])
def update_speakers(job_id):
    """Update speaker names for a completed job."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400
    
    speaker_mapping = request.json.get('speakers', {})
    
    # Update the transcript with new speaker names
    output_path = job['output_file']
    if os.path.exists(output_path):
        # Read current content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace speaker numbers with names
        for speaker_num, speaker_name in speaker_mapping.items():
            if speaker_name.strip():  # Only replace if name is provided
                content = content.replace(f"Speaker {speaker_num}:", f"{speaker_name}:")
        
        # Write updated content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return jsonify({'success': True, 'message': 'Speaker names updated'})

@app.route('/download/<job_id>')
def download_file(job_id):
    """Download the transcription file."""
    if job_id not in processing_jobs:
        # Try to find the output file directly
        output_files = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.startswith(job_id):
                output_files.append(filename)
        
        if not output_files:
            return jsonify({'error': 'Job not found'}), 404
        
        # Use the first matching file
        output_path = os.path.join(OUTPUT_FOLDER, output_files[0])
        output_filename = output_files[0]
    else:
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
        # Try to find the output file directly
        output_files = []
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.startswith(job_id):
                output_files.append(filename)
        
        if not output_files:
            return jsonify({'error': 'Job not found'}), 404
        
        # Use the first matching file
        output_path = os.path.join(OUTPUT_FOLDER, output_files[0])
        output_filename = output_files[0].replace('.txt', '.pdf')
    else:
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
                # Handle special characters for PDF
                para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
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
        # If reportlab is not installed, create a simple HTML file that can be printed as PDF
        try:
            # Create a simple HTML file that can be printed as PDF
            html_path = output_path.replace('.txt', '.html')
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Meeting Transcription</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #333; border-bottom: 2px solid #333; }}
                    .timestamp {{ color: #666; font-weight: bold; }}
                    @media print {{ body {{ margin: 20px; }} }}
                </style>
            </head>
            <body>
                <h1>Meeting Transcription</h1>
                <pre>{content}</pre>
            </body>
            </html>
            """
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return send_file(
                html_path,
                as_attachment=True,
                download_name=output_filename.replace('.pdf', '.html'),
                mimetype='text/html'
            )
        except Exception as e:
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
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
    # Initialize model on startup
    init_model()
    
    print("Starting Simple Audio to Text Converter Web Interface...")
    print("Open your browser and go to: http://localhost:5002")
    print("Note: This version works with audio files (WAV, MP3, M4A, FLAC, OGG)")
    print("For video files, you'll need to extract audio first.")
    
    app.run(debug=False, host='0.0.0.0', port=5002, threaded=True)
