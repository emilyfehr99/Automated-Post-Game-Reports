#!/usr/bin/env python3
"""
Audio to Text Converter
A free, open-source solution for converting MP4/MPV audio to text using OpenAI's Whisper model.
Perfect for transcribing work meetings with high accuracy.
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
import whisper
import torch
from moviepy.editor import VideoFileClip
import tempfile
import shutil

class AudioToTextConverter:
    def __init__(self, model_size="base", device=None):
        """
        Initialize the converter with specified Whisper model.
        
        Args:
            model_size (str): Whisper model size - tiny, base, small, medium, large
            device (str): Device to use - 'cpu', 'cuda', or None for auto-detect
        """
        self.model_size = model_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"Loading Whisper model '{model_size}' on {self.device}...")
        self.model = whisper.load_model(model_size, device=self.device)
        print("Model loaded successfully!")
    
    def extract_audio_from_video(self, video_path, output_audio_path):
        """Extract audio from video file."""
        try:
            print(f"Extracting audio from {video_path}...")
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_audio_path, verbose=False, logger=None)
            audio.close()
            video.close()
            print("Audio extraction completed!")
            return True
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    def transcribe_audio(self, audio_path, language=None, task="transcribe"):
        """
        Transcribe audio file to text with timestamps.
        
        Args:
            audio_path (str): Path to audio file
            language (str): Language code (e.g., 'en', 'es', 'fr') or None for auto-detect
            task (str): 'transcribe' or 'translate'
        
        Returns:
            dict: Transcription result with segments and text
        """
        try:
            print(f"Transcribing {audio_path}...")
            
            # Transcribe with timestamps
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                word_timestamps=True,
                verbose=False
            )
            
            return result
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    
    def format_transcription(self, result, include_timestamps=True, include_speakers=False):
        """
        Format transcription result into readable text.
        
        Args:
            result (dict): Whisper transcription result
            include_timestamps (bool): Include timestamps in output
            include_speakers (bool): Include speaker identification (if available)
        
        Returns:
            str: Formatted transcription text
        """
        if not result:
            return "Transcription failed."
        
        formatted_text = []
        
        # Add header
        formatted_text.append("=" * 60)
        formatted_text.append("MEETING TRANSCRIPTION")
        formatted_text.append("=" * 60)
        formatted_text.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        formatted_text.append(f"Model: Whisper {self.model_size}")
        formatted_text.append("")
        
        # Add full text
        formatted_text.append("FULL TRANSCRIPT:")
        formatted_text.append("-" * 40)
        formatted_text.append(result["text"])
        formatted_text.append("")
        
        if include_timestamps and "segments" in result:
            formatted_text.append("TRANSCRIPT WITH TIMESTAMPS:")
            formatted_text.append("-" * 40)
            
            for segment in result["segments"]:
                start_time = self.format_timestamp(segment["start"])
                end_time = self.format_timestamp(segment["end"])
                text = segment["text"].strip()
                
                if include_speakers and "speaker" in segment:
                    formatted_text.append(f"[{start_time} - {end_time}] Speaker {segment['speaker']}: {text}")
                else:
                    formatted_text.append(f"[{start_time} - {end_time}] {text}")
        
        return "\n".join(formatted_text)
    
    def format_timestamp(self, seconds):
        """Convert seconds to MM:SS format."""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def save_transcription(self, text, output_path):
        """Save transcription to file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Transcription saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving transcription: {e}")
            return False
    
    def process_file(self, input_path, output_path=None, language=None, 
                    include_timestamps=True, include_speakers=False):
        """
        Process a single file (video or audio) and convert to text.
        
        Args:
            input_path (str): Path to input file
            output_path (str): Path for output file (optional)
            language (str): Language code for transcription
            include_timestamps (bool): Include timestamps in output
            include_speakers (bool): Include speaker identification
        
        Returns:
            bool: Success status
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"Error: File {input_path} does not exist.")
            return False
        
        # Generate output path if not provided
        if not output_path:
            output_path = input_path.with_suffix('.txt')
        
        # Check if input is video file
        video_extensions = {'.mp4', '.mpv', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
        is_video = input_path.suffix.lower() in video_extensions
        
        temp_audio_path = None
        
        try:
            if is_video:
                # Extract audio from video
                temp_audio_path = tempfile.mktemp(suffix='.wav')
                if not self.extract_audio_from_video(str(input_path), temp_audio_path):
                    return False
                audio_path = temp_audio_path
            else:
                audio_path = str(input_path)
            
            # Transcribe audio
            result = self.transcribe_audio(audio_path, language)
            if not result:
                return False
            
            # Format and save transcription
            formatted_text = self.format_transcription(
                result, include_timestamps, include_speakers
            )
            
            return self.save_transcription(formatted_text, output_path)
            
        finally:
            # Clean up temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
    
    def process_batch(self, input_directory, output_directory=None, 
                     language=None, include_timestamps=True, include_speakers=False):
        """
        Process multiple files in a directory.
        
        Args:
            input_directory (str): Directory containing input files
            output_directory (str): Directory for output files (optional)
            language (str): Language code for transcription
            include_timestamps (bool): Include timestamps in output
            include_speakers (bool): Include speaker identification
        
        Returns:
            dict: Results summary
        """
        input_dir = Path(input_directory)
        
        if not input_dir.exists():
            print(f"Error: Directory {input_dir} does not exist.")
            return {"success": 0, "failed": 0, "errors": []}
        
        # Set output directory
        if not output_directory:
            output_directory = input_dir / "transcriptions"
        
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        # Find all supported files
        supported_extensions = {'.mp4', '.mpv', '.avi', '.mov', '.mkv', '.wmv', '.flv', 
                              '.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        
        files_to_process = []
        for ext in supported_extensions:
            files_to_process.extend(input_dir.glob(f"*{ext}"))
            files_to_process.extend(input_dir.glob(f"*{ext.upper()}"))
        
        if not files_to_process:
            print(f"No supported files found in {input_dir}")
            return {"success": 0, "failed": 0, "errors": ["No supported files found"]}
        
        print(f"Found {len(files_to_process)} files to process...")
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i, file_path in enumerate(files_to_process, 1):
            print(f"\nProcessing {i}/{len(files_to_process)}: {file_path.name}")
            
            output_path = output_dir / f"{file_path.stem}_transcript.txt"
            
            if self.process_file(
                str(file_path), str(output_path), language, 
                include_timestamps, include_speakers
            ):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to process {file_path.name}")
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description="Convert audio/video files to text using OpenAI's Whisper model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single MP4 file
  python audio_to_text_converter.py meeting.mp4
  
  # Convert with specific language and model
  python audio_to_text_converter.py meeting.mp4 --language en --model large
  
  # Process all files in a directory
  python audio_to_text_converter.py --batch /path/to/videos/
  
  # Convert without timestamps
  python audio_to_text_converter.py meeting.mp4 --no-timestamps
        """
    )
    
    parser.add_argument("input", nargs="?", help="Input file or directory path")
    parser.add_argument("-o", "--output", help="Output file or directory path")
    parser.add_argument("-l", "--language", help="Language code (e.g., 'en', 'es', 'fr')")
    parser.add_argument("-m", "--model", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--batch", action="store_true", 
                       help="Process all files in input directory")
    parser.add_argument("--no-timestamps", action="store_true", 
                       help="Exclude timestamps from output")
    parser.add_argument("--speakers", action="store_true", 
                       help="Include speaker identification (experimental)")
    parser.add_argument("--device", choices=["cpu", "cuda"], 
                       help="Device to use (auto-detect if not specified)")
    
    args = parser.parse_args()
    
    if not args.input:
        parser.print_help()
        return
    
    # Initialize converter
    converter = AudioToTextConverter(model_size=args.model, device=args.device)
    
    # Process files
    if args.batch:
        results = converter.process_batch(
            args.input, args.output, args.language,
            not args.no_timestamps, args.speakers
        )
        
        print(f"\nBatch processing completed!")
        print(f"Successfully processed: {results['success']} files")
        print(f"Failed: {results['failed']} files")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
    else:
        success = converter.process_file(
            args.input, args.output, args.language,
            not args.no_timestamps, args.speakers
        )
        
        if success:
            print("\nTranscription completed successfully!")
        else:
            print("\nTranscription failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
