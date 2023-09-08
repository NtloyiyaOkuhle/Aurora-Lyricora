# app.py
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, get_flashed_messages
from werkzeug.utils import secure_filename
import os
from audio_processor import AudioProcessor
from config import reviews_list
from reviews import Review
import datetime
import sqlite3

app = Flask(__name__)
app.config.from_object("config")

# Initialize the audio processor
audio_processor = AudioProcessor(app.config["UPLOAD_FOLDER"], app.config["OUTPUT_FOLDER"])

@app.route('/')
def index():
    try:
        # Create a connection to the database
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Retrieve reviews from the database
        cursor.execute('SELECT author, content, timestamp FROM reviews')
        reviews_data = cursor.fetchall()

        # Close the connection
        conn.close()

        # Create Review objects from the retrieved data
        reviews = [Review(content=review[1], author=review[0], timestamp=review[2]) for review in reviews_data]

        return render_template('index.html', reviews=reviews)
    except Exception as e:
        flash(str(e), 'error')
        return render_template('index.html', reviews=[])


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file:
        flash('No file uploaded', 'error')
        return jsonify({'error': 'No file uploaded'})

    if audio_processor.is_allowed_file(file.filename):
        try:
            # Inform the user that the upload process has started
            flash('Uploading...', 'info')
            
            output_filename = audio_processor.process_audio(file, request.form.get('quality'), request.form.get('audio_type'))

            # Inform the user that the mastering process has started
            flash('Mastering in progress...', 'info')

            flash('File uploaded and mastered successfully', 'success')
            flash('Mastering completed', 'info')
            return redirect(url_for('play_mastered', filename=output_filename))
        except Exception as e:
            flash(str(e), 'error')
            return jsonify({'success': False, 'error': str(e)})

    else:
        flash('Invalid file format', 'error')
        return jsonify({'error': 'Invalid file format'})

@app.route('/submit_review', methods=['POST'])
def submit_review():
    author = request.form.get('author')
    content = request.form.get('content')

    try:
        # Create a connection to the database
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Insert the new review into the database
        cursor.execute('INSERT INTO reviews (author, content) VALUES (?, ?)', (author, content))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        timestamp = datetime.datetime.now()
        new_review = Review(content, author, timestamp)

        # Return a JSON response
        return jsonify(success=True, review={
            'author': author,
            'content': content,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        flash(str(e), 'error')
        return jsonify({'success': False, 'error': str(e)})
        
@app.route('/check_mastering_status', methods=['GET'])
def check_mastering_status():
    # Implement logic to check mastering status
    mastering_completed = True  # Replace with your actual logic
    return jsonify({'mastering_completed': mastering_completed})



@app.route('/download/<format>/<filename>')
def download_audio(format, filename):
    if format == 'mp3':
        return audio_processor.download_file(filename, format='mp3')
    elif format == 'wav':
        return audio_processor.download_file(filename, format='wav')
    else:
        return "Invalid format", 400

@app.route('/play_original/<filename>')
def play_original(filename):
    return audio_processor.play_original(filename)

@app.route('/play_mastered/<filename>')
def play_mastered(filename):
    flash_messages = get_flashed_messages()
    return render_template('index.html', flash_messages=flash_messages, output_filename=filename)

@app.route('/pause_audio')
def pause_audio():
    audio_processor.pause_audio()
    return 'Audio paused'

if __name__ == '__main__':
    app.run(debug=True)
