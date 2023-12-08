import re
import math
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


def get_audio(video_url, trim, temp_dir):
    try:
        uuid = generate_unique_id()
        output_filename = attach_folder(
            f"{uuid}_output", folder_type="output")

        # if trim exists, add the args to the ydl_opts

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_filename}',
            'external_downloader': 'ffmpeg',
            'external_downloader_args': 
            trim and
            [
                '-ss', str(math.floor(trim['start_time'])),
                '-to', str(math.floor(trim['end_time'])),
                '-http_persistent', '0'
            ] or [],
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


def get_options(trim, output_file):

    if trim is None:
        return {
            "type": "aria2c",
            "options": {
                'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best[ext=mp4]',
                'outtmpl': f'{output_file}',
                'external_downloader': 'aria2c',
                'external_downloader_args': [
                    '--max-connection-per-server', '16',
                    '--throttled-rate', '100K',
                ],
            }
        }
    
    start = math.floor(trim['start_time'])
    end = math.floor(trim['end_time']) - 5

    if (end - start) > 290:
        return {
            "type": "aria2c",
            "options": {
                'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best[ext=mp4]',
                'outtmpl': f'{output_file}',
                'external_downloader': 'aria2c',
                'external_downloader_args': [
                    '--max-connection-per-server', '16',
                    '--throttled-rate', '100K',
                ],
            }
        }
    
    return {
        "type": "ffmpeg",
        "options": {
            'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best[ext=mp4]',
            'outtmpl': f'{output_file}',
            'compat_options': 'multistreams',
            'external_downloader': 'ffmpeg',
            'external_downloader_args': [
                '-threads', '4',
                '-ss', str(start),
                '-to', str(end),
            ],
        }
    }
    

def get_video(video_url, trim, quality):
    try:
        uuid = generate_unique_id()
        output_filename = attach_folder(
            f"{uuid}_output.mp4", folder_type="output")
   
        
        options = get_options(trim, output_filename)
        ydl_opts = options['options']
        
        if quality is not None:
            res = quality['resolution'].split('x')
            filesize = quality['filesize']
            ydl_opts['format'] = f'bestvideo[width<={res[0]}][height<={res[1]}][ext=mp4]+bestaudio[ext=m4a]'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            
            if options['type'] == 'aria2c':
                ffmpeg_command = [
                    'ffmpeg',
                    '-http_persistent', '0',
                    '-i', f'{output_filename}'
                ]

                if trim is not None:
                    ffmpeg_command.extend([
                        '-ss', str(math.floor(trim['start_time'])),
                        '-to', str(math.floor(trim['end_time'])),
                    ])

                ffmpeg_command.extend([
                    '-c', 'copy',
                    f'{output_filename}_trimmer.mp4',
                ])

                subprocess.run(ffmpeg_command)
                output_filename = f'{output_filename}_trimmer.mp4'       
            
            return True, output_filename

    except Exception as e:
        return False, str(e)
