import tkinter as tk
from tkinter import filedialog, messagebox
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import pyloudnorm as pyln
from spleeter.separator import Separator
import threading
import librosa
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class MasteringToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Mastering Tool")

        # Create a menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Unmastered Audio", command=self.load_audio)
        file_menu.add_command(label="Save Mastered Audio", command=self.save_audio)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        self.input_file = None
        self.output_file = None

        self.load_button = tk.Button(root, text="Load Unmastered Audio", command=self.load_audio)
        self.load_button.pack(pady=10)

        self.master_button = tk.Button(root, text="Apply Advanced Mastering", command=self.apply_advanced_mastering)
        self.master_button.pack()

        self.save_button = tk.Button(root, text="Save Mastered Audio", command=self.save_audio)
        self.save_button.pack()

        self.play_button = tk.Button(root, text="Play Mastered Audio", command=self.play_mastered_audio)
        self.play_button.pack()

        self.status_label = tk.Label(root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def load_audio(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if not self.input_file:
            return
        self.update_status("Audio loaded successfully!")

    def apply_advanced_mastering(self):
        if self.input_file is None:
            messagebox.showerror("Error", "Please load an audio file first.")
            return

        self.update_status("Applying advanced mastering...")

        threading.Thread(target=self.process_audio).start()

    def process_audio(self):
        try:
            audio, sr = self.load_audio_file(self.input_file)
            if audio is None:
                return

            processed_audio = self.apply_advanced_processing(audio, sr)
            if processed_audio is None:
                return

            self.output_file = "mastered_audio.wav"
            self.save_audio_file(processed_audio, sr, self.output_file)
            self.update_status("Advanced mastering complete!")

        except Exception as e:
            self.update_status(f"An error occurred: {str(e)}")

    def save_audio(self):
        if self.output_file:
            save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
            if save_path:
                audio, sr = self.load_audio_file(self.output_file)
                self.save_audio_file(audio, sr, save_path)

    def play_mastered_audio(self):
        if self.output_file:
            normalized_audio = self.normalize_audio(AudioSegment.from_file(self.output_file))
            play(normalized_audio)

    def load_audio_file(self, file_path):
        try:
            audio, sr = sf.read(file_path)
            return audio, sr
        except Exception as e:
            self.update_status(f"Error loading audio: {str(e)}")
            return None, None

    def save_audio_file(self, audio, sr, output_path):
        try:
            sf.write(output_path, audio, sr)
            self.update_status(f"Audio saved as: {output_path}")
        except Exception as e:
            self.update_status(f"Error saving audio: {str(e)}")

    def apply_advanced_processing(self, audio, sr):
        try:
            # Apply high-quality high-pass filter using librosa
            processed_audio = librosa.effects.preemphasis(audio)

            # Apply loudness normalization using LoudNorm
            meter = pyln.Meter(sr)
            loudness_target = -16.0  # LUFS
            integrated_loudness = meter.integrated_loudness(processed_audio)
            loudness_diff = loudness_target - integrated_loudness
            processed_audio = pyln.normalize.loudness(processed_audio, loudness_diff, target_loudness=loudness_target)

            # Apply source separation using Spleeter (5-stem model)
            separator = Separator('spleeter:5stems')
            separated_audio = separator.separate(processed_audio)

            # Process each stem separately (e.g., compression, EQ, etc.)

            # Combine the stems back together
            processed_audio = sum(separated_audio.values())

            return processed_audio

        except Exception as e:
            self.update_status(f"Error applying advanced processing: {str(e)}")
            return None

    def normalize_audio(self, audio):
        normalized_audio = normalize(audio)
        return normalized_audio

    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = MasteringToolApp(root)
    root.mainloop()
