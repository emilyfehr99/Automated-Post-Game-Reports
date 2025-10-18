# 🎤 Audio to Text Converter - Web Interface

A beautiful, modern web interface for converting MP4/MPV files to text using OpenAI's Whisper model. Upload your meeting recordings and download accurate transcriptions instantly!

## ✨ Features

- **🌐 Web Interface**: Beautiful, responsive design that works on any device
- **📁 Drag & Drop**: Simply drag your files onto the page
- **⚡ Real-time Progress**: See processing status with live updates
- **📄 Multiple Formats**: Download as TXT or PDF
- **🎯 High Accuracy**: Uses OpenAI's Whisper model for best results
- **🔄 Batch Processing**: Handle multiple files efficiently
- **🌍 Multi-language**: Support for 10+ languages with auto-detection
- **📱 Mobile Friendly**: Works perfectly on phones and tablets

## 🚀 Quick Start

### Option 1: Easy Launch (Recommended)
```bash
python run_web_app.py
```
This will automatically:
- Check and install dependencies
- Start the web server
- Open your browser to the interface

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements_web.txt

# Start the web server
python audio_converter_web.py
```

Then open your browser and go to: **http://localhost:5000**

## 🎯 How to Use

1. **Upload File**: Drag & drop or click to select your MP4/MPV file
2. **Choose Options**: Select model size, language, and formatting options
3. **Process**: Watch the real-time progress as your file is converted
4. **Download**: Get your transcription as TXT or PDF

## 📊 Model Selection Guide

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| **Tiny** | 39 MB | ⚡⚡⚡ | Basic | Quick previews |
| **Base** | 74 MB | ⚡⚡ | Good | General meetings |
| **Small** | 244 MB | ⚡ | Better | Important content |
| **Medium** | 769 MB | 🐌 | High | Critical meetings |
| **Large** | 1550 MB | 🐌🐌 | Best | Maximum accuracy |

## 🌍 Supported Languages

- **Auto-detect** (recommended)
- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean, Chinese

## 📁 Supported File Formats

**Video**: MP4, MPV, AVI, MOV, MKV, WMV, FLV  
**Audio**: WAV, MP3, M4A, FLAC, OGG

## 🎨 Interface Features

### Upload Section
- Drag & drop support
- File validation
- Size limits (500MB max)
- Format checking

### Processing Options
- Model size selection
- Language settings
- Timestamp inclusion
- Speaker identification

### Progress Tracking
- Real-time status updates
- Progress bar
- Processing stages:
  - Loading AI model
  - Extracting audio
  - Converting speech to text

### Download Options
- TXT format (plain text)
- PDF format (formatted document)
- Automatic file naming

## 🔧 Technical Details

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB for models
- **GPU**: Optional but recommended

### File Limits
- **Maximum file size**: 500MB
- **Processing time**: 1-10 minutes depending on file size and model
- **Concurrent jobs**: Limited by system resources

### Security & Privacy
- **Local processing**: All files stay on your computer
- **No data sharing**: Your audio never leaves your device
- **Automatic cleanup**: Files are deleted after 24 hours
- **Secure uploads**: Files are validated and sanitized

## 🛠️ Advanced Usage

### Custom Configuration
Edit `audio_converter_web.py` to modify:
- File size limits
- Supported formats
- Processing options
- Cleanup intervals

### API Endpoints
The web interface also provides REST API endpoints:

- `POST /upload` - Upload and process file
- `GET /status/<job_id>` - Check processing status
- `GET /download/<job_id>` - Download TXT file
- `GET /download_pdf/<job_id>` - Download PDF file
- `GET /jobs` - List all jobs
- `GET /cleanup` - Clean old files

### Integration
You can integrate the converter into other applications:

```python
import requests

# Upload file
with open('meeting.mp4', 'rb') as f:
    response = requests.post('http://localhost:5000/upload', 
                           files={'file': f},
                           data={'model': 'base', 'language': 'en'})

job_id = response.json()['job_id']

# Check status
status = requests.get(f'http://localhost:5000/status/{job_id}').json()

# Download when complete
if status['status'] == 'completed':
    txt_file = requests.get(f'http://localhost:5000/download/{job_id}')
    with open('transcript.txt', 'wb') as f:
        f.write(txt_file.content)
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements_web.txt
```

**"FFmpeg not found"**
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`
- Windows: Download from https://ffmpeg.org/

**Out of memory errors**
- Use smaller model (tiny or base)
- Close other applications
- Process shorter files

**Slow processing**
- Use GPU if available
- Choose smaller model
- Ensure good CPU performance

### Performance Tips

- **Best accuracy**: Large model + GPU
- **Fastest processing**: Tiny model + CPU
- **Balanced**: Base or Small model
- **Large files**: Consider splitting into smaller segments

## 📱 Mobile Usage

The web interface is fully responsive and works great on mobile devices:

- Touch-friendly drag & drop
- Optimized for small screens
- Works on iOS and Android
- No app installation required

## 🔒 Security Notes

- Files are processed locally on your machine
- No internet connection required after setup
- Automatic file cleanup prevents storage issues
- All uploads are validated for security

## 🎉 Enjoy Your Free Transcription Service!

No more paying for expensive transcription services. This web interface gives you professional-quality speech-to-text conversion completely free, running on your own computer with full privacy and control.

---

**Need help?** Check the troubleshooting section or review the command-line version for advanced options.
