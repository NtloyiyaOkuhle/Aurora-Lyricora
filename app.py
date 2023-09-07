# app.py
from flask import Flask, render_template, request, flash, send_file, jsonify,redirect,url_for
from werkzeug.utils import secure_filename
import os
from audio_processor import AudioProcessor

app = Flask(__name__)
app.config.from_object("config")

# Initialize the audio processor
audio_processor = AudioProcessor(app.config["UPLOAD_FOLDER"], app.config["OUTPUT_FOLDER"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file:
        flash('No file uploaded', 'error')
        return jsonify({'error': 'No file uploaded'})

    if audio_processor.is_allowed_file(file.filename):
        try:
            output_filename = audio_processor.process_audio(file, request.form.get('quality'), request.form.get('audio_type'))
            flash('File uploaded and mastered successfully', 'success')

            # Pass the output_filename as a parameter when redirecting to the play routes
            return redirect(url_for('play_mastered', filename=output_filename))
        except Exception as e:
            flash(str(e), 'error')
            return jsonify({'error': str(e)})
    else:
        flash('Invalid file format', 'error')
        return jsonify({'error': 'Invalid file format'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/play_original/<filename>')
def play_original(filename):
    return audio_processor.play_original(filename)


@app.route('/play_mastered/<filename>')
def play_mastered(filename):
    return audio_processor.play_mastered(filename)

@app.route('/pause_audio')
def pause_audio():
    audio_processor.pause_audio()
    return 'Audio paused'

if __name__ == '__main__':
    app.run(debug=True)
