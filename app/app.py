import datetime
from datetime import timedelta
import tempfile
import math
import stripe
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from supabase import create_client
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from .internals.utils import (
    generate_unique_id,
    get_audio,
    get_video,
    handle_response,
    get_video_information
)

app = FastAPI()
load_dotenv()

# GET ENVS
STRIPE_SECTET_KEY = os.getenv("STRIPE_SECTET_KEY")
SUPA_BASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPA_BASE_KEY = os.getenv("SUPABASE_KEY")
FRONTEND_URL = os.getenv('FRONTEND_URL')

supabase_client = create_client(SUPA_BASE_URL, SUPA_BASE_KEY)

origins = [
    "https://vid-slicer.vercel.app",
    "https://www.downloadbazar.com",
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
    quality: dict


@app.get("/")
def status():
    return f"The API is working fine - {datetime.datetime.now()}".upper()


@app.get("/order/success")
async def order_success(session_id: str =
                        Query(...,
                              title="Stripe Session",
                              description="Id of the Stripe session"
                              ), user_id: str = Query(...,
                                                      title="User ID",
                                                      description="Id of the user"
                                                      )):
    try:
        stripe.api_key = STRIPE_SECTET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        supabase_client.table("UserProfile").update({
            "customer_id": session['customer'],
        }).eq('user_id', user_id).execute()
        return RedirectResponse(url=FRONTEND_URL)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@app.get('/stripe/customer/subscriptions')
async def get_user_subscription(customer_id: str =
                                Query(...,
                                      title="Stripe Customer Id",
                                      description="Id of the Stripe Customer for that user"
                                      )):
    try:
        stripe.api_key = STRIPE_SECTET_KEY
        subscriptions = stripe.Subscription.list(customer=customer_id)

        for subscription in subscriptions.data:
            subscription_status = subscription.status
            if subscription_status == "active":
                data = {
                    "subscription_id": subscription.id,
                    "status": True,
                    "plan": subscription.plan
                }
                return JSONResponse(status_code=200, content=data)

        return JSONResponse(status_code=200, content={
            "status": False, "plan": None, "subscription_id": None})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


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
