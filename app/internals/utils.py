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


def get_audio(video_url, start_time, end_time, temp_dir):
    try:
        uuid = generate_unique_id()
        download_location =  os.path.join(temp_dir, f"raw")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_location}/{uuid}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)

            if start_time < 0:
                start_time = 0
            if end_time > info_dict['duration']:
                end_time = info_dict['duration']

            filename = f"{download_location}/{uuid}.mp3"
            output_filename = attach_folder(f"{uuid}_output.mp3", folder_type="output")

            cmd = [
                "ffmpeg",
                "-ss", str(start_time),
                "-i", filename,
                "-to", str(end_time),
                "-c:v", "copy",
                "-c:a", "copy",
                output_filename
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True, output_filename

    except Exception as e:
        return False, str(e)


def get_video(video_url, start_time, end_time, **kwargs):
    try:
        uuid = generate_unique_id()
        output_filename = attach_folder(
            f"{uuid}_output.mp4", folder_type="output")
        quality = kwargs.get('quality', "")

        ydl_opts = {
            'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best[ext=mp4]',
            'outtmpl': f'{output_filename}',
            'external_downloader': 'ffmpeg',
            'external_downloader_args': [
                '-ss', str(start_time),
                '-to', str(end_time),
            ],
        }

        if quality:
            if quality == '144':
                ydl_opts['format'] = 'bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[height<=144]/best[ext=mp4]'
            elif quality == '240':
                ydl_opts['format'] = 'bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240]/best[ext=mp4]'
            elif quality == '360':
                ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best[ext=mp4]'
            elif quality == '480':
                ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best[ext=mp4]'
            elif quality == '720':
                ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best[ext=mp4]'
            elif quality == '1080':
                ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best[ext=mp4]'
            elif quality == '1440':
                ydl_opts['format'] = 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440]/best[ext=mp4]'
        else:
            return False, "Video Quality is not defined"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return True, output_filename

    except Exception as e:
        return False, str(e)
