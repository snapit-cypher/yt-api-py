# create a new virtual environment with the following command

python3.10 -m venv venv

# install the requiremtns

pip install -r reqirements.txt

# setup ffpep

apt-get update && apt-get install -y ffmpeg

# run the project

python main.py

## Request example

```json
// POST /download
{
"url": "https://www.youtube.com/watch?v=d1h2_TygQYM",
"quality": {
    "filesize": 49442983,
    "resolution": "1920x1080",
    "format_note": "1080p"
}, // selected quality is optional and can be removed
"trim": {
    "start_time": "00:00:00",
    "end_time": "00:00:10"
}, // Trim is optional and can be removed

"audio": true // Audio is false by default (for video) and can be removed
}
```

```json
// GET /video_info
HOST:PORT/video_info?url=https://www.youtube.com/watch?v=d1h2_TygQYM
```
