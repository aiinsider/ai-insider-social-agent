"""
Posts to LinkedIn (personal profile or organization page) via the UGC Posts API.
Requires an access token with w_member_social (personal) or
w_organization_social (company page) scope, and the author's URN.
"""

import logging
import requests

import config

log = logging.getLogger("linkedin")

API_URL = "https://api.linkedin.com/v2/ugcPosts"


def post(text: str, link: str) -> dict:
    full_text = f"{text}\n\n{link}"

    if config.DRY_RUN:
        log.info(f"[DRY RUN] Would post to LinkedIn:\n{full_text}\n")
        return {"dry_run": True, "text": full_text}

    headers = {
        "Authorization": f"Bearer {config.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    body = {
        "author": config.LINKEDIN_AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": full_text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    resp = requests.post(API_URL, headers=headers, json=body)
    resp.raise_for_status()
    data = resp.json()
    log.info(f"Posted to LinkedIn: {data}")
    return data
