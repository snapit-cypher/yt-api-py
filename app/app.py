import datetime
import tempfile
import math
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from internals.utils import (
    generate_unique_id,
    get_audio,
    get_video,
    handle_response
)

app = FastAPI()


class Item(BaseModel):
    url: str
    audio: bool
    start_time: float
    end_time: float
    quality: str


@app.get("/")
def status():
    return f"The API is working fine - {datetime.datetime.now()}".upper()


@app.post("/youtube-downloader/")
async def youtube_downloader(item: Item):
    try:
        url = item.url
        audio = item.audio
        start = math.floor(item.start_time)
        end = math.floor(item.end_time)

        if audio:
            with tempfile.TemporaryDirectory() as temp_dir:
                status, filename = get_audio(url, start, end, temp_dir)
                if status:
                    return FileResponse(filename)
                else:
                    raise Exception(filename)

        else:
            quality = item.quality
            status, filename = get_video(
                url, start, end, quality=quality)
            if status:
                return FileResponse(filename)
            else:
                raise Exception(filename)

    except Exception as e:
        return handle_response(False, str(e))
