"""
Turns a raw article (title + RSS summary) into platform-specific post copy
using Claude. Mixes two angles per config.CONTENT_MIX:
  - "summary": straight, factual recap of the news
  - "commentary": a short original take/analysis angle on why it matters

Important: this generates ORIGINAL text inspired by the headline/summary —
it does not and should not reproduce article text verbatim. Always credit
the source and link back to the original article.
"""

import json
import logging
import random

from anthropic import Anthropic

import config

log = logging.getLogger("content_generator")

client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

PLATFORM_STYLE = {
    "twitter": "Concise, punchy, no hashtag spam (max 1-2 relevant hashtags). Hook in the first line.",
    "linkedin": "Professional but conversational tone, can include a brief 'why this matters for businesses/professionals' angle. 2-4 short paragraphs.",
    "facebook": "Friendly, accessible, slightly more casual than LinkedIn. Encourage engagement with a light question at the end.",
    "instagram": "Caption written for a visual-first audience: strong hook line, short paragraphs, end with 3-6 relevant hashtags.",
}


def _build_prompt(article: dict, angle: str, platform: str) -> str:
    limit = config.PLATFORM_LIMITS[platform]
    style = PLATFORM_STYLE[platform]

    angle_instruction = (
        "Write a factual, neutral recap of this news."
        if angle == "summary"
        else "Write a short original opinion/analysis take on why this development matters — "
             "your own commentary, not just a recap."
    )

    return f"""You are drafting a social media post about an AI/tech news story for {platform}.

Article title: {article['title']}
Article source: {article['source']}
RSS summary (for context only — do not quote it verbatim): {article['summary'][:600]}

Instructions:
- {angle_instruction}
- Platform style: {style}
- Hard limit: {limit} characters, including any hashtags. Stay under this.
- Do NOT reproduce sentences from the summary verbatim — write entirely in your own words.
- Do NOT invent facts, numbers, or quotes not implied by the title/summary above.
- Do NOT include the raw URL in the body text (it will be appended separately).
- Return ONLY the post text, nothing else — no preamble, no quotation marks around it.
"""


def generate_post(article: dict, platform: str, angle: str = None) -> str:
    angle = angle or random.choice(config.CONTENT_MIX)
    prompt = _build_prompt(article, angle, platform)

    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return text


def generate_all_platform_posts(article: dict) -> dict:
    """Returns {platform: post_text} for every enabled platform."""
    angle = random.choice(config.CONTENT_MIX)  # same angle across platforms for one article
    posts = {}
    for platform in config.ENABLED_PLATFORMS:
        try:
            posts[platform] = generate_post(article, platform, angle)
        except Exception as e:
            log.error(f"Failed to generate {platform} post for '{article['title']}': {e}")
    return posts
