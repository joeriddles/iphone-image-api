import datetime
import io
import json
import random
from functools import lru_cache
from typing import Any

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Response
from html2image import Html2Image
from jinja2 import Environment, PackageLoader, select_autoescape
from PIL import Image
from starlette.responses import RedirectResponse
from zoneinfo import ZoneInfo

IPHONE_12_PLUS_DIMENSIONS = (1170, 2532)
default_w = IPHONE_12_PLUS_DIMENSIONS[0]
default_h = IPHONE_12_PLUS_DIMENSIONS[1]

env = Environment(
    loader=PackageLoader("main"),
    autoescape=select_autoescape(),
)

app = FastAPI()

tz = ZoneInfo("America/Los_Angeles")


@app.get("/")
def root(
    w: int = default_w,
    h: int = default_h,
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
    today = get_today()
    image_url = get_votd_image_url(today)
    return RedirectResponse(image_url)


@app.get("/votd/html/")
def votd_html():
    today = get_today()
    verse_ref, verse = get_votd_verse(today)
    template = env.get_template("verse.html")
    verse_ref, verse = get_votd_verse(today)
    content = template.render(verse_ref=verse_ref, verse=verse)
    return Response(content)


@app.get("/votd/text/")
def votd_text(
    w: int = default_w,
    h: int = default_h,
):
    if w * h > 10_000_000:
        return "No thanks fam"

    today = get_today()
    verse_ref, verse = get_votd_verse(today)
    image_filename = render_verse(verse_ref, verse, w, h)
    file = open(image_filename, "rb")
    image = file.read()
    return Response(content=image, media_type="image/png")


def get_votd_image_url(today: datetime.date) -> str:
    next_data = get_votd_data(today)
    votds = next_data["props"]["pageProps"]["images"][0]["renditions"]
    votd = votds[-1]
    image_url: str = votd["url"]
    image_url = image_url.replace("//", "https://", 1)
    return image_url


def get_votd_verse(today: datetime.date) -> tuple[str, str]:
    next_data = get_votd_data(today)
    verse_data = next_data["props"]["pageProps"]["verses"][0]
    ref = verse_data["reference"]["human"]
    verse = verse_data["content"]
    return (ref, verse)


# @lru_cache
def render_verse(verse_ref: str, verse: str, width: int, height: int) -> str:
    today = get_today()

    template = env.get_template("verse.html")
    verse_ref, verse = get_votd_verse(today)
    content = template.render(verse_ref=verse_ref, verse=verse)

    hti = Html2Image(size=(width, height), browser="chromium")
    filenames = hti.screenshot(html_str=content, save_as=f"{today}.png")
    filename = filenames[0]
    print(f"Generated {filename}")
    return filenames[0]


@lru_cache
def get_votd_data(today: datetime.date) -> dict[str, Any]:
    del today  # just using for LRU caching

    response = requests.get("https://www.bible.com/verse-of-the-day")
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    next_data = soup.find_all(attrs={"id": "__NEXT_DATA__"})[0].text
    next_data = json.loads(next_data)
    return next_data


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


def get_today() -> datetime.date:
    return datetime.datetime.now(tz).date()
