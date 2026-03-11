# pipeline/manifest.py
"""Track generated parts for incremental regeneration."""
import hashlib
import json
import os


class Manifest:
    """Tracks which parts have been generated and with what parameters."""

    def __init__(self, path: str):
        self._path = path
        self._entries: dict[str, str] = {}  # part_id -> param_hash
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self._entries = data.get("parts", {})

    def _hash_params(self, params: dict) -> str:
        """Deterministic hash of parameters."""
        canonical = json.dumps(params, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def is_generated(self, part_id: str, params: dict) -> bool:
        """Check if a part was already generated with these exact params."""
        expected_hash = self._hash_params(params)
        return self._entries.get(part_id) == expected_hash

    def mark_generated(self, part_id: str, params: dict) -> None:
        """Mark a part as generated."""
        self._entries[part_id] = self._hash_params(params)

    def save(self) -> None:
        """Persist manifest to disk."""
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w") as f:
            json.dump({"parts": self._entries}, f, indent=2)

    def is_empty(self) -> bool:
        return len(self._entries) == 0

    def count(self) -> int:
        return len(self._entries)
