"""Persistence helpers for prompted-writing verification credentials."""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import config

_lock = threading.Lock()


def _read_credentials() -> dict[str, str]:
    path: Path = config.VERIFIED_CREATORS_FILE
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(
        isinstance(creator_id, str) and isinstance(timestamp, str)
        for creator_id, timestamp in data.items()
    ):
        raise ValueError(f"Invalid verified-creator data in {path}")
    return data


def is_verified(creator_id: str) -> bool:
    with _lock:
        return creator_id in _read_credentials()


def add_verified_creator(creator_id: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path: Path = config.VERIFIED_CREATORS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        credentials = _read_credentials()
        credentials[creator_id] = timestamp
        temporary_path = path.with_suffix(path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(credentials, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, path)
    return timestamp
