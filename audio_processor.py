# app.py
from pydub import AudioSegment
import pygame
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, get_flashed_messages, send_file
import numpy as np
from scipy import signal
import sqlite3

class AudioProcessor:
    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        pygame.mixer.init()

    def is_allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'mp3', 'wav'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def process_audio(self, file, quality, audio_type):
        try:
            if not os.path.exists(self.upload_folder):
                os.makedirs(self.upload_folder)
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            filename = secure_filename(file.filename)
            uploaded_filepath = os.path.join(self.upload_folder, filename)
            file.save(uploaded_filepath)

            audio = AudioSegment.from_file(uploaded_filepath)

            # Inform the user that the upload process has completed
            flash('Upload completed', 'info')

            # Apply high-pass filter on side image (make low frequencies mono)
            audio = self.apply_high_pass_filter(audio, cutoff_freq=130)
            flash('High-pass filter applied', 'info')

            # Use two limiters in series
            audio = self.apply_limiter(audio, release_time=30)  # First limiter
            flash('First limiter applied', 'info')

            audio = self.apply_limiter(audio, release_time=100)  # Second limiter
            flash('Second limiter applied', 'info')

            # Apply multi-band expander
            audio = self.apply_multiband_expander(audio)
            flash('Multi-band expander applied', 'info')

            # Export audio in a lossless format (WAV) with high-quality settings
            output_filename = f"mastered_{quality}_{audio_type}_{filename}"
            output_filepath = os.path.join(self.output_folder, output_filename)

            # Use 24-bit export for higher quality
            audio.export(output_filepath, format="wav", parameters=["-b:a", "24k"])
            flash('Mastering completed', 'info')

            # Set the mastering_completed flag to True
            mastering_completed = True

            return output_filename, mastering_completed

        except Exception as e:
            flash(f'Error processing audio: {str(e)}', 'error')
            return None, False

        except Exception as e:
            flash(f'Error processing audio: {str(e)}', 'error')
            return None, False

    def download_file(self, filename, format):
        try:
            output_filepath = os.path.join(self.output_folder, filename)
            if os.path.exists(output_filepath):
                # Check the requested format and convert if necessary
                if format == 'mp3':
                    output_audio = AudioSegment.from_wav(output_filepath)
                    mp3_output_filepath = os.path.join(self.output_folder, f"{filename.split('.')[0]}.mp3")
                    output_audio.export(mp3_output_filepath, format="mp3")
                    return send_file(mp3_output_filepath, as_attachment=True, download_name=f"{filename.split('.')[0]}.mp3")
                elif format == 'wav':
                    return send_file(output_filepath, as_attachment=True, download_name=filename)
                else:
                    flash('Unsupported format', 'error')
                    return "Unsupported format", 400
            else:
                flash('Mastered file not found', 'error')
                return "Mastered file not found", 404

        except Exception as e:
            flash(f'Error downloading file: {str(e)}', 'error')
            return None

    def play_original(self, filename):
        try:
            original_filepath = os.path.join(self.upload_folder, filename)
            if os.path.exists(original_filepath):
                audio = AudioSegment.from_file(original_filepath)
                return send_file(audio.export(format="wav"), as_attachment=True, download_name=filename)
            else:
                flash('Original file not found', 'error')
                return "Original file not found", 404

        except Exception as e:
            flash(f'Error playing original file: {str(e)}', 'error')
            return None

    def play_mastered(self, filename):
        try:
            mastered_filepath = os.path.join(self.output_folder, filename)
            if os.path.exists(mastered_filepath):
                audio = AudioSegment.from_file(mastered_filepath)
                return send_file(audio.export(format="wav"), as_attachment=True, download_name=filename)
            else:
                flash('Mastered file not found', 'error')
                return "Mastered file not found", 404

        except Exception as e:
            flash(f'Error playing mastered file: {str(e)}', 'error')
            return None

    def pause_audio(self):
        try:
            pygame.mixer.music.pause()
            return 'Audio paused'

        except Exception as e:
            flash(f'Error pausing audio: {str(e)}', 'error')
            return None

    def apply_high_pass_filter(self, audio, cutoff_freq):
        try:
            # Apply high-pass filter using PyDub's high_pass_filter method
            audio = audio.high_pass_filter(cutoff_freq)

            return audio

        except Exception as e:
            flash(f'Error applying high-pass filter: {str(e)}', 'error')
            return audio

    def apply_limiter(self, audio, release_time):
        try:
            # Apply a limiter effect by adjusting the volume
            max_volume = audio.max_possible_amplitude
            audio = audio - max_volume  # Reduce volume to avoid clipping

            return audio

        except Exception as e:
            flash(f'Error applying limiter: {str(e)}', 'error')
            return audio

    def apply_multiband_expander(self, audio):
        try:
            # Apply a multi-band expander for dynamic sound (placeholder)
            # In a professional setup, you would use dedicated plugins or tools for this
            # This is a simplified example using PyDub
            return audio  # Placeholder for multi-band expander logic

        except Exception as e:
            flash(f'Error applying multi-band expander: {str(e)}', 'error')
            return audio

    def eq_match_advanced(self, audio, reference_track):
        try:
            # Load the reference track
            reference_audio = AudioSegment.from_file(reference_track)

            # Convert both audio tracks to numpy arrays for spectral analysis
            audio_np = np.array(audio.get_array_of_samples())
            reference_np = np.array(reference_audio.get_array_of_samples())

            # Calculate the spectral envelope of both tracks
            audio_envelope = pyo.FFT(audio_np).abs().smooth(0.01)
            reference_envelope = pyo.FFT(reference_np).abs().smooth(0.01)

            # Apply EQ matching by equalizing the audio based on the reference envelope
            matched_audio = audio.apply_gain(reference_envelope / audio_envelope)

            return matched_audio

        except Exception as e:
            flash(f'Error applying advanced EQ matching: {str(e)}', 'error')
            return audio

    def advanced_parallel_compression(self, audio, compression_ratio=4.0, blend_factor=0.5):
        try:
            # Create a compressor with customizable settings
            compressor = pyo.Compressor(threshold=-18, ratio=compression_ratio, attack=0.01, release=0.1)

            # Apply heavy compression
            compressed_audio = compressor(audio)

            # Blend the compressed audio with the original
            blended_audio = (audio * (1 - blend_factor)) + (compressed_audio * blend_factor)

            return blended_audio

        except Exception as e:
            flash(f'Error applying advanced parallel compression: {str(e)}', 'error')
            return audio

    def advanced_adjust_limiter_release(self, audio, release_time_ms):
        try:
            # Convert release_time_ms to time in seconds
            release_time_sec = release_time_ms / 1000.0

            # Apply precise release time adjustment
            audio = audio.fade_out(release_time_sec)

            return audio

        except Exception as e:
            flash(f'Error applying advanced limiter release adjustment: {str(e)}', 'error')
            return audio

app = Flask(__name__)
app.config.from_object("config")

if __name__ == '__main__':
    app.run(debug=True)
