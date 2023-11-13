import datetime
import tempfile
import math
from fastapi import FastAPI, Query
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .internals.utils import (
    generate_unique_id,
    get_audio,
    get_video,
    handle_response,
    get_video_information
)

app = FastAPI()

origins = [
    "https://vid-slicer.vercel.app",
    "http://vid-slicer.vercel.app",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    url: str
    audio: bool
    start_time: float
    end_time: float
    quality: str


@app.get("/")
def status():
    return f"The API is working fine - {datetime.datetime.now()}".upper()


@app.get("/video_info")
async def info_handler(url: str = Query(..., title="Item Name", description="Enter the item name")):
    try:
        status, options = get_video_information(url)
        if status:
            return JSONResponse(status_code=200, content={ "data": options })
        else:
            raise Exception(options)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

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
                    return FileResponse(filename, media_type="audio/mp3")
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
        return JSONResponse(status_code=400, content={"error": str(e)})

