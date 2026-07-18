"""Network-free reference for independent channel progress.

Replace ``sender`` with a real API adapter. The state contract prevents one
failed channel from causing duplicate delivery through channels that already
succeeded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable


def message_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class ChannelState:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> dict[str, dict[str, int | bool]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def deliver(
        self,
        channel: str,
        text: str,
        sender: Callable[[str], None],
        chunk_size: int = 200,
    ) -> bool:
        key = f"{channel}:{message_id(text)}"
        progress = self.data.setdefault(key, {"next": 0, "done": False})
        if progress["done"]:
            return False

        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] or [""]
        for index in range(int(progress["next"]), len(chunks)):
            sender(chunks[index])
            progress["next"] = index + 1
            self._save()

        progress["done"] = True
        self._save()
        return True

