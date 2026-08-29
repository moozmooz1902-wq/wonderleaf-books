"""Run state: what we have already made, so angles and hooks do not repeat."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import ROOT


class State:
    def __init__(self, path=None):
        self.path = Path(path) if path else ROOT / "out" / "state.json"
        self.data = {"runs": [], "videos": []}
        if self.path.exists():
            with self.path.open(encoding="utf-8") as fh:
                self.data = json.load(fh)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2)
        tmp.replace(self.path)

    # -- angle rotation ---------------------------------------------------

    def recent_pairs(self, cooldown_days):
        """(product_id, angle) pairs used inside the cooldown window."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=cooldown_days)
        pairs = set()
        for v in self.data["videos"]:
            try:
                when = datetime.fromisoformat(v["created_at"])
            except (KeyError, ValueError):
                continue
            if when >= cutoff:
                pairs.add((v.get("product_id"), v.get("angle")))
        return pairs

    def used_hooks(self, limit=120):
        """Recent hook lines, so the writer can be told not to repeat them."""
        return [v["hook"] for v in self.data["videos"][-limit:] if v.get("hook")]

    def next_index(self):
        return len(self.data["videos"]) + 1

    # -- recording --------------------------------------------------------

    def record_video(self, entry):
        entry.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self.data["videos"].append(entry)

    def record_run(self, summary):
        summary.setdefault("at", datetime.now(timezone.utc).isoformat())
        self.data["runs"].append(summary)
