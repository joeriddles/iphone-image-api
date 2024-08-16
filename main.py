from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo
import io
import json
import random


from bs4 import BeautifulSoup
from PIL import Image
from fastapi import FastAPI, Response
from starlette.responses import RedirectResponse
import requests

app = FastAPI()

tz = ZoneInfo("America/Los_Angeles")


@app.get("/")
def root(
    w: int = 200,
    h: int = 200,
    c: str | None = None,
):
    if w * h > 10_000_000:
        return "No thanks fam"

    if not c:
        c = random_color()
    if c and len(c) == 6:
        c = "#" + c

    image = generate_image(width=w, height=h, color=c)
    return Response(content=image, media_type="image/png")


@app.get("/votd/")
def votd():
    today = datetime.now(tz).date()
    image_url = get_votd_image_url(today)
    return RedirectResponse(image_url)


@lru_cache
def get_votd_image_url(today: datetime) -> str:
    del today  # just using for LRU caching

    response = requests.get("https://www.bible.com/verse-of-the-day")
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    next_data = soup.find_all(attrs={"id": "__NEXT_DATA__"})[0].text
    next_data = json.loads(next_data)
    votds = next_data["props"]["pageProps"]["images"][0]["renditions"]
    votd = votds[-1]
    image_url: str = votd["url"]
    image_url = image_url.replace("//", "https://", 1)
    return image_url


def generate_image(
    width: int,
    height: int,
    color: str,
) -> bytes:
    image = Image.new("RGB", (width, height), color)

    fp = io.BytesIO()
    image.save(fp, format="PNG")
    fp.seek(0)
    image_bytes = fp.read()
    return image_bytes


HEX = "0123456789abcdef"


def random_color() -> str:
    return "#" + "".join(random.choice(HEX) for _ in range(6))
