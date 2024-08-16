import io
import random

from PIL import Image
from fastapi import FastAPI, Response

app = FastAPI()


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
