#!/usr/bin/env python3
"""
GUI Interface for Audio to Text Converter
A user-friendly graphical interface for the audio to text converter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import json
from audio_to_text_converter import AudioToTextConverter

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio to Text Converter")
        self.root.geometry("800x600")
        
        # Converter instance
        self.converter = None
        self.processing = False
        
        # Create GUI elements
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Audio to Text Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=1, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path_var, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Model selection
        ttk.Label(options_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(options_frame, textvariable=self.model_var, 
                                  values=["tiny", "base", "small", "medium", "large"],
                                  state="readonly", width=15)
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Language selection
        ttk.Label(options_frame, text="Language:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.language_var = tk.StringVar(value="auto")
        language_combo = ttk.Combobox(options_frame, textvariable=self.language_var,
                                     values=["auto", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                                     state="readonly", width=10)
        language_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Checkboxes
        self.timestamps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include timestamps", 
                       variable=self.timestamps_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.speakers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Include speakers", 
                       variable=self.speakers_var).grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=2)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.convert_button = ttk.Button(buttons_frame, text="Convert", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Settings", command=self.show_settings).pack(side=tk.LEFT)
        
        # Output text area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_file(self):
        """Browse for input file."""
        filetypes = [
            ("All supported", "*.mp4;*.mpv;*.avi;*.mov;*.mkv;*.wmv;*.flv;*.wav;*.mp3;*.m4a;*.flac;*.ogg"),
            ("Video files", "*.mp4;*.mpv;*.avi;*.mov;*.mkv;*.wmv;*.flv"),
            ("Audio files", "*.wav;*.mp3;*.m4a;*.flac;*.ogg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select input file",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
            # Auto-generate output filename
            if not self.output_path_var.get():
                input_path = Path(filename)
                output_path = input_path.with_suffix('.txt')
                self.output_path_var.set(str(output_path))
    
    def browse_output(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            title="Save transcription as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            self.output_path_var.set(filename)
    
    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        if self.processing:
            messagebox.showwarning("Warning", "Conversion is already in progress!")
            return
        
        # Validate inputs
        if not self.file_path_var.get():
            messagebox.showerror("Error", "Please select an input file!")
            return
        
        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Please specify an output file!")
            return
        
        # Start conversion in separate thread
        self.processing = True
        self.convert_button.config(state="disabled")
        self.progress_bar.start()
        self.progress_var.set("Initializing...")
        self.status_var.set("Processing...")
        
        thread = threading.Thread(target=self.convert_file)
        thread.daemon = True
        thread.start()
    
    def convert_file(self):
        """Convert file (runs in separate thread)."""
        try:
            # Initialize converter
            self.progress_var.set("Loading Whisper model...")
            self.converter = AudioToTextConverter(model_size=self.model_var.get())
            
            # Get language setting
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            
            # Convert file
            self.progress_var.set("Converting audio to text...")
            success = self.converter.process_file(
                self.file_path_var.get(),
                self.output_path_var.get(),
                language,
                self.timestamps_var.get(),
                self.speakers_var.get()
            )
            
            if success:
                self.progress_var.set("Conversion completed successfully!")
                self.status_var.set("Ready")
                
                # Show result in output area
                self.root.after(0, self.show_result)
            else:
                self.progress_var.set("Conversion failed!")
                self.status_var.set("Error occurred")
                self.root.after(0, lambda: messagebox.showerror("Error", "Conversion failed! Check the output for details."))
        
        except Exception as e:
            self.progress_var.set(f"Error: {str(e)}")
            self.status_var.set("Error occurred")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        
        finally:
            self.processing = False
            self.root.after(0, self.conversion_finished)
    
    def conversion_finished(self):
        """Called when conversion is finished."""
        self.convert_button.config(state="normal")
        self.progress_bar.stop()
    
    def show_result(self):
        """Show conversion result in output area."""
        try:
            if os.path.exists(self.output_path_var.get()):
                with open(self.output_path_var.get(), 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(1.0, content)
                
                messagebox.showinfo("Success", f"Transcription saved to:\n{self.output_path_var.get()}")
            else:
                messagebox.showerror("Error", "Output file was not created!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read output file: {str(e)}")
    
    def clear_all(self):
        """Clear all fields."""
        self.file_path_var.set("")
        self.output_path_var.set("")
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set("Ready")
        self.status_var.set("Ready")
    
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        ttk.Label(settings_window, text="Audio to Text Converter Settings", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Device selection
        device_frame = ttk.Frame(settings_window)
        device_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(device_frame, text="Device:").pack(side=tk.LEFT)
        self.device_var = tk.StringVar(value="auto")
        device_combo = ttk.Combobox(device_frame, textvariable=self.device_var,
                                   values=["auto", "cpu", "cuda"], state="readonly")
        device_combo.pack(side=tk.RIGHT)
        
        # Info text
        info_text = """
Model Size Guide:
• tiny: Fastest, least accurate (~39 MB)
• base: Good balance of speed and accuracy (~74 MB)
• small: Better accuracy, slower (~244 MB)
• medium: High accuracy, slower (~769 MB)
• large: Best accuracy, slowest (~1550 MB)

Language:
• auto: Automatically detect language
• en: English, es: Spanish, fr: French, etc.

Device:
• auto: Automatically choose best device
• cpu: Force CPU usage
• cuda: Use GPU if available
        """
        
        info_label = ttk.Label(settings_window, text=info_text, justify=tk.LEFT)
        info_label.pack(padx=20, pady=10)
        
        # Close button
        ttk.Button(settings_window, text="Close", 
                  command=settings_window.destroy).pack(pady=10)
    
    def load_settings(self):
        """Load settings from file."""
        settings_file = "audio_converter_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                self.model_var.set(settings.get("model", "base"))
                self.language_var.set(settings.get("language", "auto"))
                self.timestamps_var.set(settings.get("timestamps", True))
                self.speakers_var.set(settings.get("speakers", False))
            except Exception as e:
                print(f"Could not load settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        settings = {
            "model": self.model_var.get(),
            "language": self.language_var.get(),
            "timestamps": self.timestamps_var.get(),
            "speakers": self.speakers_var.get()
        }
        
        try:
            with open("audio_converter_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    def on_closing(self):
        """Handle window closing."""
        self.save_settings()
        self.root.destroy()

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
