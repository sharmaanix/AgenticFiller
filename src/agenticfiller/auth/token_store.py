"""Per-user OAuth token persistence.

One JSON file per Gmail address, stored under ``TOKEN_DIR`` (see config).
Handles silent refresh — callers always get a valid Credentials object
or None.
"""

from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from agenticfiller.config import GMAIL_SCOPES, TOKEN_DIR


def _safe_id(user_id: str) -> str:
    """Convert email to a safe filename stem (reversible)."""
    return user_id.replace("@", "__at__").replace(".", "__dot__")


def _unsafe_id(safe: str) -> str:
    """Reverse :func:`_safe_id`."""
    return safe.replace("__at__", "@").replace("__dot__", ".")


class TokenStore:
    """Persists and retrieves per-user OAuth2 tokens from disk."""

    def __init__(self, token_dir: Path = TOKEN_DIR) -> None:
        self.token_dir = token_dir
        self.token_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        return self.token_dir / f"{_safe_id(user_id)}.json"

    def load(self, user_id: str) -> Credentials | None:
        """Load credentials, refreshing if expired. None when unavailable."""
        p = self._path(user_id)
        if not p.exists():
            return None
        with open(p) as f:
            data = json.load(f)
        # Strip our internal metadata before handing to google-auth
        data.pop("_user_id", None)
        creds = Credentials.from_authorized_user_info(data, GMAIL_SCOPES)
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.save(user_id, creds)
            except Exception:
                return None
        return creds if creds.valid else None

    def save(self, user_id: str, creds: Credentials) -> None:
        data = json.loads(creds.to_json())
        data["_user_id"] = user_id  # so list_users can recover it
        with open(self._path(user_id), "w") as f:
            json.dump(data, f, indent=2)

    def delete(self, user_id: str) -> None:
        p = self._path(user_id)
        if p.exists():
            p.unlink()

    def is_authenticated(self, user_id: str) -> bool:
        return self.load(user_id) is not None

    def list_users(self) -> list[str]:
        users: list[str] = []
        for f in self.token_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                users.append(data.get("_user_id", _unsafe_id(f.stem)))
            except Exception:
                pass
        return users
