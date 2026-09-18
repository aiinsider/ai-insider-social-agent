"""
Posts to a Facebook Page's feed using the Graph API.
Requires a Page Access Token with pages_manage_posts permission.
"""

import logging
import requests

import config

log = logging.getLogger("facebook")

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"


def post(text: str, link: str) -> dict:
    full_text = f"{text}\n\n{link}"

    if config.DRY_RUN:
        log.info(f"[DRY RUN] Would post to Facebook Page:\n{full_text}\n")
        return {"dry_run": True, "text": full_text}

    url = f"{GRAPH_API_BASE}/{config.FACEBOOK_PAGE_ID}/feed"
    resp = requests.post(url, data={
        "message": full_text,
        "access_token": config.FACEBOOK_PAGE_ACCESS_TOKEN,
    })
    resp.raise_for_status()
    data = resp.json()
    log.info(f"Posted to Facebook: {data}")
    return data
