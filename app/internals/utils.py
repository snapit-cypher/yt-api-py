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
        output_filename = attach_folder(
            f"{uuid}_output", folder_type="output")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_filename}',
            'external_downloader': 'ffmpeg',
            'external_downloader_args': [
                '-ss', str(start_time),
                '-to', str(end_time),
            ],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return True, f"{output_filename}.mp3"

    except Exception as e:
        return False, str(e)


def get_video_information(video_url):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            result = ydl.extract_info(video_url, download=False)

        audio_formats = []
        video_formats = []

        if 'formats' in result:
            for format_item in result['formats']:
                if format_item.get("audio_ext", "none") != "none" and format_item.get("ext", "N/A") != "mp4":
                    audio_formats.append({
                        "filesize": format_item.get("filesize", "N/A")
                    })

                if format_item.get("video_ext", "none") != "none" and format_item.get("filesize", "none") != ("none" or None):
                    filesize = format_item.get("filesize", "N/A"),
                    resolution = format_item.get("resolution", "N/A"),
                    format_note = format_item.get("format_note", "N/A")

                    if not "N/A" in [filesize, format_note, resolution]:
                        video_formats.append({
                            "filesize": format_item.get("filesize", "N/A"),
                            "resolution": format_item.get("resolution", "N/A"),
                            "format_note": format_item.get("format_note", "N/A")
                        })
        max_audio_format = max(
            audio_formats, key=lambda x: x['filesize'], default=None)
        return True, {"audio_format": max_audio_format, "video_formats": video_formats}

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
            res = quality['resolution'].split('x')
            filesize = quality['filesize']
            ydl_opts['format'] = f'bestvideo[width<={res[0]}][height<={res[1]}][ext=mp4][filesize<={filesize}]+bestaudio[ext=m4a]'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return True, output_filename

    except Exception as e:
        return False, str(e)
