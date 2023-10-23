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

def attach_folder(file_name, folder_type):
    return f"{DOWNLOAD_FOLDER}/{'raw' if folder_type == 'raw' else 'output'}/{file_name}"

def handle_response(status, data):
    return {
        'error': not status,
        'data': data,
    }

def get_audio(video_url, start_time, end_time):
    try:
        uuid = generate_unique_id()
        download_location = attach_folder(uuid, folder_type='raw')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_location}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)

            # Check if 'start_time' and 'end_time' are within the video duration
            if start_time < 0:
                start_time = 0
            if end_time > info_dict['duration']:
                end_time = info_dict['duration']

            filename = attach_folder(f"{uuid}.mp3", folder_type="raw")
            trimmed_filename = attach_folder(
                f"{uuid}_trimmed.mp3", folder_type="output")

            cmd = [
                "ffmpeg",
                "-ss", str(start_time),
                "-i", filename,
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

def get_video(video_url, start_time, end_time, **kwargs):
    try:
        uuid = generate_unique_id()
        download_location = attach_folder(uuid, folder_type='raw')
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': f'{download_location}.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            # Chec if 'start_time' and 'end_time' are within the video duration
            if start_time < 0:
                start_time = 0
            if end_time > info_dict['duration']:
                end_time = info_dict['duration']

            filename = attach_folder(f"{uuid}.mp4", folder_type="raw")
            trimmed_filename = attach_folder(
                f"{uuid}_trimmed.mp4", folder_type="output")

            cmd = [
                "ffmpeg",
                "-ss", str(start_time),
                "-i", filename,
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
