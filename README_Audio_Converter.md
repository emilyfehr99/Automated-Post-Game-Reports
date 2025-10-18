# Audio to Text Converter

A free, open-source solution for converting MP4/MPV audio to text using OpenAI's Whisper model. Perfect for transcribing work meetings with high accuracy.

## Features

- **High Accuracy**: Uses OpenAI's Whisper model for state-of-the-art speech recognition
- **Multiple Formats**: Supports MP4, MPV, AVI, MOV, MKV, WMV, FLV, WAV, MP3, M4A, FLAC, OGG
- **Batch Processing**: Convert multiple files at once
- **Timestamps**: Include precise timestamps in your transcriptions
- **Multiple Languages**: Auto-detect or specify language
- **User-Friendly**: Both command-line and graphical interfaces
- **Free**: No subscription fees or usage limits

## Quick Start

### 1. Installation

Run the setup script to install all dependencies:

```bash
python setup_audio_converter.py
```

Or install manually:

```bash
pip install -r requirements_audio_converter.txt
```

### 2. Basic Usage

#### Command Line Interface

Convert a single file:
```bash
python audio_to_text_converter.py meeting.mp4
```

Convert with specific options:
```bash
python audio_to_text_converter.py meeting.mp4 --model large --language en --output meeting_notes.txt
```

Process all files in a directory:
```bash
python audio_to_text_converter.py --batch /path/to/videos/
```

#### Graphical Interface

Launch the GUI:
```bash
python audio_converter_gui.py
```

## Model Selection

Choose the right model for your needs:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | ~39 MB | Fastest | Basic | Quick previews |
| base | ~74 MB | Fast | Good | General use |
| small | ~244 MB | Medium | Better | Important meetings |
| medium | ~769 MB | Slow | High | Critical content |
| large | ~1550 MB | Slowest | Best | Maximum accuracy |

## Command Line Options

```
python audio_to_text_converter.py [input] [options]

Arguments:
  input                 Input file or directory path

Options:
  -o, --output         Output file or directory path
  -l, --language       Language code (e.g., 'en', 'es', 'fr')
  -m, --model          Whisper model size (tiny, base, small, medium, large)
  --batch              Process all files in input directory
  --no-timestamps      Exclude timestamps from output
  --speakers           Include speaker identification (experimental)
  --device             Device to use (cpu, cuda)
```

## Examples

### Single File Conversion
```bash
# Basic conversion
python audio_to_text_converter.py meeting.mp4

# High accuracy with English language
python audio_to_text_converter.py meeting.mp4 --model large --language en

# Without timestamps
python audio_to_text_converter.py meeting.mp4 --no-timestamps
```

### Batch Processing
```bash
# Process all videos in a folder
python audio_to_text_converter.py --batch /Users/username/meetings/

# Batch with specific output directory
python audio_to_text_converter.py --batch /Users/username/meetings/ -o /Users/username/transcripts/
```

### Advanced Usage
```bash
# Force GPU usage for faster processing
python audio_to_text_converter.py meeting.mp4 --device cuda --model large

# Translate to English
python audio_to_text_converter.py spanish_meeting.mp4 --language es --task translate
```

## Output Format

The converter generates text files with:

1. **Header Information**: Date, model used, file processed
2. **Full Transcript**: Complete text without timestamps
3. **Timestamped Version**: Text with precise timestamps

Example output:
```
============================================================
MEETING TRANSCRIPTION
============================================================
Generated: 2024-01-15 14:30:25
Model: Whisper base

FULL TRANSCRIPT:
----------------------------------------
Good morning everyone, welcome to today's team meeting...

TRANSCRIPT WITH TIMESTAMPS:
----------------------------------------
[00:00 - 00:05] Good morning everyone, welcome to today's team meeting.
[00:05 - 00:12] Let's start by reviewing our progress from last week.
[00:12 - 00:18] I'd like to hear updates from each team member.
```

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended for large models)
- **Storage**: 2GB free space for models
- **GPU**: Optional but recommended for faster processing

## Troubleshooting

### Common Issues

1. **"No module named 'whisper'"**
   - Run: `pip install openai-whisper`

2. **"FFmpeg not found"**
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

3. **Out of memory errors**
   - Use a smaller model (tiny or base)
   - Close other applications
   - Process shorter audio segments

4. **Slow processing**
   - Use GPU if available: `--device cuda`
   - Use smaller model for faster processing
   - Ensure good CPU performance

### Performance Tips

- **For best accuracy**: Use `large` model with GPU
- **For speed**: Use `tiny` or `base` model
- **For balance**: Use `small` or `medium` model
- **Batch processing**: More efficient for multiple files

## File Size Guidelines

| Audio Length | Recommended Model | Approximate Time |
|--------------|-------------------|------------------|
| < 5 minutes  | base              | 1-2 minutes      |
| 5-30 minutes | small             | 3-10 minutes     |
| 30+ minutes  | medium/large      | 10-30 minutes    |

## Privacy & Security

- **Local Processing**: All transcription happens on your computer
- **No Internet Required**: After initial model download
- **No Data Sharing**: Your audio files never leave your device
- **Open Source**: Full source code available for inspection

## Advanced Features

### Custom Language Models
You can fine-tune Whisper models for specific domains or accents by following OpenAI's documentation.

### Integration
The converter can be integrated into other applications using the `AudioToTextConverter` class:

```python
from audio_to_text_converter import AudioToTextConverter

converter = AudioToTextConverter(model_size="base")
result = converter.transcribe_audio("meeting.wav")
print(result["text"])
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the command-line help: `python audio_to_text_converter.py --help`
3. Ensure all dependencies are properly installed

## License

This project is open source and free to use. The Whisper model is released under the MIT License.

---

**Enjoy your free, accurate audio-to-text conversion!** 🎉
