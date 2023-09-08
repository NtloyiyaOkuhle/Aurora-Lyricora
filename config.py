# config.py
import os
from reviews import Review

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
SECRET_KEY = 'your_secret_key'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# Create a list to store reviews
reviews_list = []

# Ensure the upload and output folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
