import io

from PIL import Image
from fastapi import FastAPI, Response

width, height = 200, 200
color = (255, 0, 0)  # Red color
image = Image.new("RGB", (width, height), color)

fp = io.BytesIO()
image.save(fp, format="PNG")
fp.seek(0)
image_bytes = fp.read()

app = FastAPI()


@app.get("/")
def root():
    return Response(content=image_bytes, media_type="image/png")
