"""
Runs ONE full cycle: fetch news -> pick unposted articles -> generate
platform-specific copy -> post everywhere -> log what was posted.

Meant to be triggered by cron a few times a day (see README) rather than
run as a persistent loop — that keeps each run short, restart-safe, and
easy to monitor.

Usage:
    python run_cycle.py
"""

import logging
import sys

import config
from news_fetcher import fetch_recent_articles
from content_generator import generate_all_platform_posts
from posted_log import PostedLog

from platforms import twitter, facebook, linkedin, instagram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("run_cycle")

POSTER = {
    "twitter": lambda post_text, article: twitter.post(post_text, article["link"]),
    "facebook": lambda post_text, article: facebook.post(post_text, article["link"]),
    "linkedin": lambda post_text, article: linkedin.post(post_text, article["link"]),
    "instagram": lambda post_text, article: instagram.post(
        post_text, article["link"], article["title"], article["source"]
    ),
}


def run():
    if config.DRY_RUN:
        log.warning(
            "Running in DRY_RUN mode — nothing will actually be posted. "
            "Set LIVE_POSTING_ENABLED=true in .env AND CONFIRM_LIVE_POSTING=True "
            "in config.py to go live."
        )

    if not config.ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY not set in .env. Cannot generate content. Exiting.")
        sys.exit(1)

    posted_log = PostedLog(config.POSTED_LOG_PATH)
    articles = fetch_recent_articles()

    if not articles:
        log.info("No new unposted articles found this cycle.")
        return

    to_post = articles[: config.POSTS_PER_CYCLE]
    log.info(f"Selected {len(to_post)} article(s) to post this cycle.")

    for article in to_post:
        log.info(f"Generating posts for: {article['title']} ({article['source']})")
        posts = generate_all_platform_posts(article)

        succeeded_platforms = []
        for platform in config.ENABLED_PLATFORMS:
            post_text = posts.get(platform)
            if not post_text:
                continue
            try:
                POSTER[platform](post_text, article)
                succeeded_platforms.append(platform)
            except Exception as e:
                log.error(f"Failed to post to {platform} for '{article['title']}': {e}")

        if succeeded_platforms and not config.DRY_RUN:
            posted_log.mark_posted(article["link"], succeeded_platforms, article["title"])
        elif config.DRY_RUN:
            log.info(f"[DRY RUN] Would mark as posted on: {succeeded_platforms or config.ENABLED_PLATFORMS}")


if __name__ == "__main__":
    run()
