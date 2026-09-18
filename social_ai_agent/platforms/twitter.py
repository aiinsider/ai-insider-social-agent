"""
Posts to X (Twitter) using OAuth 1.0a user-context credentials via tweepy.
Requires a developer app with "Read and Write" permissions.
"""

import logging
import tweepy

import config

log = logging.getLogger("twitter")


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
    )


def post(text: str, link: str) -> dict:
    full_text = f"{text}\n\n{link}"

    if config.DRY_RUN:
        log.info(f"[DRY RUN] Would post to Twitter:\n{full_text}\n")
        return {"dry_run": True, "text": full_text}

    client = _client()
    resp = client.create_tweet(text=full_text)
    log.info(f"Posted to Twitter: {resp}")
    return resp.data
