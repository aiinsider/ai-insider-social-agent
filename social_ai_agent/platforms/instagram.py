"""
Posts to an Instagram Business/Creator account via the Graph API.
Requires the IG account linked to a Facebook Page, and a token with
instagram_content_publish permission.

Instagram posting is two steps:
  1. Create a media container (image_url + caption)
  2. Publish that container
"""

import logging
import time
import requests

import config
import image_generator

log = logging.getLogger("instagram")

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"


def post(text: str, link: str, article_title: str, article_source: str) -> dict:
    caption = f"{text}\n\n🔗 Link in bio / comments: {link}"

    if config.DRY_RUN:
        log.info(f"[DRY RUN] Would generate image + post to Instagram:\n{caption}\n")
        return {"dry_run": True, "text": caption}

    image_url = image_generator.generate_and_host_image(article_title, article_source)

    # Step 1: create container
    container_resp = requests.post(
        f"{GRAPH_API_BASE}/{config.INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": config.FACEBOOK_PAGE_ACCESS_TOKEN,
        },
    )
    container_resp.raise_for_status()
    creation_id = container_resp.json()["id"]

    # Instagram needs a moment to process the container before publishing
    time.sleep(5)

    # Step 2: publish
    publish_resp = requests.post(
        f"{GRAPH_API_BASE}/{config.INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": config.FACEBOOK_PAGE_ACCESS_TOKEN,
        },
    )
    publish_resp.raise_for_status()
    data = publish_resp.json()
    log.info(f"Posted to Instagram: {data}")
    return data
