import os
import re
import datetime
import yt_dlp
import uuid
import subprocess
from .constants import DOWNLOAD_FOLDER

def generate_unique_id():
    return str(uuid.uuid4())

def clean_filename(filename):
    # Define a regular expression to match characters that should be removed
    invalid_chars = r'[\/:*?"<>|]'

    # Replace invalid characters with underscores
    cleaned_filename = re.sub(invalid_chars, '_', filename)

    # Remove leading and trailing spaces
    cleaned_filename = cleaned_filename.strip()

    # Remove consecutive underscores and replace with a single underscore
    cleaned_filename = re.sub(r'[_]+', '_', cleaned_filename)

    return cleaned_filename.replace(' ', '_')

def attach_folder(file_name):
    return f"{DOWNLOAD_FOLDER}/{file_name}"

def get_audio(video_url, start_time, end_time):
    try:
        uuid = generate_unique_id()
        ydl_opts = {
            'format': 'bestaudio/best',
            'keepvideo': False,
            'outtmpl': f'{DOWNLOAD_FOLDER}/{uuid}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            ydl.download([video_url])

            filename = attach_folder(f"{uuid}.mp3")
            trimmed_filename = f"{filename[:-4]}_trimmed.mp3"
            
            cmd = [
                "ffmpeg",
                "-i", filename,
                "-ss", str(start_time),
                "-to", str(end_time),
                "-c:v", "copy",
                "-c:a", "copy",
                trimmed_filename
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            os.remove(filename)
            return True, trimmed_filename

    except Exception as e:
        return False, str(e)

def handle_response(status, data):
    return {
        'error': not status,
        'data': data,
    }
