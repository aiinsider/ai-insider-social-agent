"""
Central configuration for the social media agent.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---- Content generation ----
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"

# ---- News sources (RSS feeds — swap in whatever you trust) ----
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
]

# How many candidate articles to pull per cycle, and how many to actually post
ARTICLES_PER_CYCLE = 10
POSTS_PER_CYCLE = 2  # keep this modest — this is how many posts go out per run

# ---- Content mix ----
# "summary" = straight news recap, "commentary" = AI's own take/analysis angle
CONTENT_MIX = ["summary", "commentary"]

# ---- Platform character/style limits ----
PLATFORM_LIMITS = {
    "twitter": 260,       # leave headroom under 280 for a link
    "linkedin": 1300,     # LinkedIn rewards longer, more professional posts
    "facebook": 500,
    "instagram": 2200,    # caption limit; keep actual copy shorter in practice
}

# ---- Platforms to post to ----
ENABLED_PLATFORMS = ["twitter", "facebook", "linkedin", "instagram"]

# ---- Credentials ----
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

# ---- Safety switch ----
# Two gates, like the forex bot: env var AND this file. Both must allow live
# posting or the bot only prints what it *would* post (DRY_RUN).
LIVE_POSTING_ENABLED_ENV = os.getenv("LIVE_POSTING_ENABLED", "false").lower() == "true"
CONFIRM_LIVE_POSTING = False  # flip to True in code once you trust the output

DRY_RUN = not (LIVE_POSTING_ENABLED_ENV and CONFIRM_LIVE_POSTING)

# ---- Storage ----
POSTED_LOG_PATH = "posted_log.json"
