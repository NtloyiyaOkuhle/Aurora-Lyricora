from pydub import AudioSegment
import pygame
import os
from werkzeug.utils import secure_filename
from flask import send_file
import numpy as np
from scipy import signal

class AudioProcessor:
    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        pygame.mixer.init()

    def is_allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'mp3', 'wav'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def process_audio(self, file, quality, audio_type):
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        filename = secure_filename(file.filename)
        uploaded_filepath = os.path.join(self.upload_folder, filename)
        file.save(uploaded_filepath)

        audio = AudioSegment.from_file(uploaded_filepath)

        # Apply high-pass filter on side image (make low frequencies mono)
        audio = self.apply_high_pass_filter(audio, cutoff_freq=130)

        # Use two limiters in series
        audio = self.apply_limiter(audio, release_time=30)  # First limiter
        audio = self.apply_limiter(audio, release_time=100)  # Second limiter

        # Apply multi-band expander
        audio = self.apply_multiband_expander(audio)

        # Export audio in a lossless format (WAV)
        output_filename = f"mastered_{quality}_{audio_type}_{filename}"
        output_filepath = os.path.join(self.output_folder, output_filename)
        audio.export(output_filepath, format="wav")

        return output_filename

    def download_file(self, filename):
        return send_file(os.path.join(self.output_folder, filename), as_attachment=True)

    def play_original(self, filename):
        original_filepath = os.path.join(self.upload_folder, filename)
        if os.path.exists(original_filepath):
            pygame.mixer.music.load(original_filepath)
            pygame.mixer.music.play()
            return "Original audio is playing"
        else:
            return "Original file not found", 404

    def play_mastered(self, filename):
        mastered_filepath = os.path.join(self.output_folder, filename)
        if os.path.exists(mastered_filepath):
            pygame.mixer.music.load(mastered_filepath)
            pygame.mixer.music.play()
            return "Mastered audio is playing"
        else:
            return "Mastered file not found", 404

    def pause_audio(self):
        pygame.mixer.music.pause()


    def apply_high_pass_filter(self, audio, cutoff_freq):
        # Apply a high-pass filter on the side image (make low frequencies mono)
        channels = audio.split_to_mono()
        side_image = channels[1]  # Assuming the right channel is the side image

        # Convert to NumPy array for processing
        side_image_array = np.array(side_image.get_array_of_samples())

        # Apply high-pass filter
        side_image_array = self.high_pass_filter(side_image_array, cutoff_freq)

        # Convert back to PyDub audio
        side_image = AudioSegment(
            side_image_array.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=side_image.sample_width,
            channels=1  # Convert to mono
        )

        # Combine the processed side image with the original left channel
        processed_audio = AudioSegment.from_mono_audiosegments(channels[0], side_image)
        return processed_audio


    def apply_limiter(self, audio, release_time):
        # Apply a limiter with a specified release time (in milliseconds)
        return audio.limit(0, release_time=release_time)


    def apply_multiband_expander(self, audio):
        # Apply a multi-band expander for dynamic sound (placeholder)
        # In a professional setup, you would use dedicated plugins or tools for this
        # This is a simplified example using PyDub
        return audio  # Placeholder for multi-band expander logic


    def high_pass_filter(self, audio_array, cutoff_freq):
        # Apply a high-pass filter to an audio array (placeholder)
        # In a professional setup, you would use dedicated signal processing libraries
        # This is a simplified example using NumPy
        nyquist_rate = 0.5 * audio_array.shape[0]
        normal_cutoff = cutoff_freq / nyquist_rate
        b, a = signal.butter(1, normal_cutoff, btype='high', analog=False)
        filtered_audio = signal.lfilter(b, a, audio_array)
        return filtered_audio