"""Central configuration.

All magic numbers, paths, and scopes live here so the rest of the
package never hard-codes them. Override with environment variables
where appropriate.
"""

from pathlib import Path

# ── OAuth scopes ────────────────────────────────────────────────────────────
# gmail.readonly: list/read messages + download attachments
# userinfo.email + openid: confirm which Gmail address consented
GMAIL_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

# ── Local OAuth callback server ─────────────────────────────────────────────
CALLBACK_PORT: int = 8080
REDIRECT_URI: str = f"http://localhost:{CALLBACK_PORT}/oauth/callback"

# ── Filesystem locations ────────────────────────────────────────────────────
# Stored under $HOME so they survive `git clean` and aren't committed.
APP_DIR: Path = Path.home() / ".agenticfiller"
TOKEN_DIR: Path = APP_DIR / "tokens"
ATTACHMENT_DIR: Path = APP_DIR / "attachments"
