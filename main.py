import json
import os
import random
import string
import aiofiles

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from typing import Annotated
import motor.motor_asyncio
app = FastAPI()

templates = Jinja2Templates(directory='templates')


client = motor.motor_asyncio.AsyncIOMotorClient(
    host=os.getenv("MONGO_HOST", "localhost"),
    port=int(os.getenv("MONGO_PORT",27017)),
    username=os.getenv("MONGO_USERNAME", "root"),
    password=os.getenv("MONGO_PASSWORD", "example")
    # authSource= os.getenv("MONGO_AUTH_SOURCE", "root" )
)

@app.get("/")
async def index(request:Request):
    return templates.TemplateResponse(request=request, name='index.html')

@app.post("/")
async def get_url(url: Annotated[str, Form()]):
    short_url = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for _ in range(6))
    new_doc = {"short_url": short_url, "long_url": url}
    await client["FAP_short_url"]["urls"].insert_one(new_doc)

    return {'result': short_url}


@app.get("/{short_url}")
async def say_hello(short_url: str):
    url_document = await client["FAP_short_url"]["urls"].find_one({"short_url": short_url})
    res_url = url_document["long_url"]
    url_document["hits_counter"] = url_document.get("hits_counter", 0) +1
    #
    # hits_counter = url_document.get("hits_counter", 0)
    # url_document["hits_counter"] = hits_counter + 1
    await client["FAP_short_url"]["urls"].replace_one({"_id": url_document["_id"]}, url_document)
    return RedirectResponse(res_url)
# await client.FAP_short_url.urls
