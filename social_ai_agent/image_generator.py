"""
Instagram requires an image for feed posts, and the Graph API needs a
PUBLIC URL for that image (not a local file or base64 blob).

This module does two things:
  1. Renders a simple headline card as a .png using Pillow (swap this for
     a real design/template or an image-gen API if you want nicer visuals)
  2. Uploads it to Imgur (free, works with just a Client ID) to get a
     public URL Instagram can fetch

Swap `upload_image()` for S3/Cloudinary/your own hosting if preferred —
it just needs to return a public HTTPS URL.
"""

import logging
import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

import config

log = logging.getLogger("image_generator")

CARD_SIZE = (1080, 1080)  # Instagram square
BG_COLOR = (17, 17, 17)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (110, 130, 255)


def _load_font(size: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_headline_card(title: str, source: str) -> bytes:
    img = Image.new("RGB", CARD_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Accent bar
    draw.rectangle([(0, 0), (CARD_SIZE[0], 12)], fill=ACCENT_COLOR)

    # Wrapped headline
    title_font = _load_font(64)
    wrapped = textwrap.wrap(title, width=22)[:6]  # cap lines so it fits
    y = 300
    for line in wrapped:
        draw.text((80, y), line, font=title_font, fill=TEXT_COLOR)
        y += 78

    # Source label
    source_font = _load_font(32)
    draw.text((80, CARD_SIZE[1] - 120), f"via {source}", font=source_font, fill=ACCENT_COLOR)
    draw.text((80, CARD_SIZE[1] - 70), "AI News", font=source_font, fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def upload_image(image_bytes: bytes) -> str:
    """Uploads to Imgur (anonymous, Client-ID only) and returns the public URL."""
    if not config.IMGUR_CLIENT_ID:
        raise RuntimeError("IMGUR_CLIENT_ID not set in .env — required for Instagram image hosting.")

    resp = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {config.IMGUR_CLIENT_ID}"},
        files={"image": image_bytes},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["link"]


def generate_and_host_image(title: str, source: str) -> str:
    image_bytes = render_headline_card(title, source)
    return upload_image(image_bytes)
