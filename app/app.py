
import datetime
import tempfile
import os
import time
import asyncio
from fastapi import FastAPI, Query, Request
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
from internals.utils import (
    get_audio,
    get_video,
    get_video_information
)
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

REQUEST_TIMEOUT_ERROR = 300 # Threshold of 300 seconds

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://slicetube.io",
    "https://www.slicetube.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Quality(BaseModel):
    filesize: int
    resolution: str
    format_note: str

class Trim(BaseModel):
    start_time: float
    end_time: float

class Item(BaseModel):
    url: str
    audio: bool = False
    trim: Optional[Trim] = None
    quality: Optional[Quality] = None

# Adding a middleware returning a 504 error if the request processing time is above a certain threshold
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        print("Request processing time limit set to", REQUEST_TIMEOUT_ERROR)
        
        start_time = time.time()
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_ERROR)

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        return JSONResponse({'detail': 'Request processing time excedeed limit',
                             'processing_time': process_time},
                            status_code=HTTP_504_GATEWAY_TIMEOUT)

@app.get("/")
def status():
    return f"The API is working fine - {datetime.datetime.now()}".upper()

@app.get("/video_info")
async def info_handler(url: str = Query(..., title="Item Name", description="Enter the item name")):
    try:
        status, options = get_video_information(url)
        if status:
            return JSONResponse(status_code=200, content={"data": options})
        else:
            raise Exception(options)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.post("/download/")
async def youtube_downloader(item: Item):
    try:
        url = item.url
        audio = item.audio or False # default is video

        trim = dict(item.trim) if item.trim else None

        if audio:
            with tempfile.TemporaryDirectory() as temp_dir:
                status, filename = get_audio(url, trim, temp_dir)
                if status:
                    task = BackgroundTask(delete_file, filename)
                    return FileResponse(filename, media_type="audio/mp3", background=task)
                else:
                    # delete file anyway
                    os.remove(filename)
                    raise Exception(filename)

        else:
            quality = dict(item.quality)

            status, filename = get_video(
                url, trim, quality)
            if status:
                task = BackgroundTask(delete_file, filename)
                return FileResponse(filename, media_type="video/mp4", background=task)
            else:
                # delete file anyway
                os.remove(filename)
                raise Exception(filename)

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# create file deletion background task, to be run after response is sent
async def delete_file(filename):
    print(f"Deleting file {filename} from disk")
    os.remove(filename)
