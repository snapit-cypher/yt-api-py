from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from internals.utils import (
    generate_unique_id,
    get_audio,
    handle_response
)

app = FastAPI()


class Item(BaseModel):
    url: str
    audio: bool
    start_time: float
    end_time: float


@app.get("/")
def status():
    return f"The API is working fine - {datetime.datetime.now()}".upper()

@app.post("/youtube-downloader/")
async def youtube_downloader(item: Item):
    try:
        url = item.url
        audio = item.audio
        start = item.start_time
        end = item.end_time

        if audio:
            status, filename = get_audio(url, start, end)
            if status:
                return FileResponse(filename)
            else:
                raise Exception(filename)

    except Exception as e:
        return handle_response(False, str(e))
