"""
Tracks which article links have already been posted, so the bot never
posts the same story twice across platforms or across restarts.
"""

import json
import os
from datetime import datetime, timezone


class PostedLog:
    def __init__(self, path: str):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)

    def already_posted(self, link: str) -> bool:
        return link in self._data

    def mark_posted(self, link: str, platforms: list, title: str = ""):
        self._data[link] = {
            "title": title,
            "platforms": platforms,
            "posted_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()
