"""
Pulls recent articles from configured RSS feeds and filters out ones
already posted (tracked in posted_log.json).
"""

import logging
import feedparser
from datetime import datetime, timezone, timedelta

import config
from posted_log import PostedLog

log = logging.getLogger("news_fetcher")


def fetch_recent_articles(max_age_hours: int = 48) -> list:
    """Returns a list of dicts: {title, link, summary, published, source}"""
    posted = PostedLog(config.POSTED_LOG_PATH)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    articles = []

    for feed_url in config.RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            log.warning(f"Failed to parse feed {feed_url}: {e}")
            continue

        source_name = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            link = entry.get("link")
            if not link or posted.already_posted(link):
                continue

            published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            if published_struct:
                published_dt = datetime(*published_struct[:6], tzinfo=timezone.utc)
                if published_dt < cutoff:
                    continue
            else:
                published_dt = None

            articles.append({
                "title": entry.get("title", "").strip(),
                "link": link,
                "summary": entry.get("summary", "").strip(),
                "published": published_dt.isoformat() if published_dt else None,
                "source": source_name,
            })

    # Newest first when we have timestamps
    articles.sort(key=lambda a: a["published"] or "", reverse=True)
    return articles[: config.ARTICLES_PER_CYCLE]
