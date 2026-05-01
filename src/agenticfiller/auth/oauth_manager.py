"""Browser-based OAuth2 flow orchestration.

Spins up a tiny local HTTP server on :data:`CALLBACK_PORT`, opens the
user's browser to the Google consent screen, captures the authorization
code, exchanges it for tokens, and persists them via :class:`TokenStore`.
"""

from __future__ import annotations

import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from agenticfiller.config import CALLBACK_PORT, GMAIL_SCOPES, REDIRECT_URI

from .token_store import TokenStore


class OAuthManager:
    """Manages the full OAuth2 browser-redirect flow for a single user.

    Example:
        manager = OAuthManager(client_id, client_secret)
        creds = manager.run_auth_flow("alice@gmail.com")   # blocks
        creds = manager.get_credentials("alice@gmail.com")  # later calls
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.store = TokenStore()
        self._auth_code: str | None = None
        self._auth_error: str | None = None

    def get_credentials(self, user_id: str) -> Credentials | None:
        return self.store.load(user_id)

    def run_auth_flow(self, user_id: str, timeout: int = 120) -> Credentials:
        """Open a browser for the user to approve Gmail access.

        Blocks for up to *timeout* seconds waiting for the OAuth
        callback, persists tokens, and returns the resulting
        :class:`Credentials`.
        """
        flow = self._build_flow()
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            state=user_id,
            include_granted_scopes="true",
        )

        self._auth_code = None
        self._auth_error = None

        httpd = HTTPServer(("localhost", CALLBACK_PORT), self._callback_handler())
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()

        print(f"\nAuthentication required for {user_id}")
        print("Opening browser — if it doesn't launch, visit:")
        print(f"  {auth_url}\n")
        webbrowser.open(auth_url)

        deadline = time.monotonic() + timeout
        while self._auth_code is None and self._auth_error is None:
            if time.monotonic() > deadline:
                httpd.shutdown()
                raise TimeoutError(
                    f"OAuth flow timed out after {timeout}s — no browser response."
                )
            time.sleep(0.4)

        httpd.shutdown()

        if self._auth_error:
            raise PermissionError(f"OAuth denied: {self._auth_error}")

        flow.fetch_token(code=self._auth_code)
        creds = flow.credentials
        self.store.save(user_id, creds)
        return creds

    # ── Private helpers ─────────────────────────────────────────────────────

    def _build_flow(self) -> Flow:
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        }
        return Flow.from_client_config(
            client_config, scopes=GMAIL_SCOPES, redirect_uri=REDIRECT_URI
        )

    def _callback_handler(self) -> type[BaseHTTPRequestHandler]:
        """Return a request handler class that captures the auth code."""
        manager = self

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path != "/oauth/callback":
                    self._respond(404, b"Not found")
                    return

                params = parse_qs(parsed.query)
                if "code" in params:
                    manager._auth_code = params["code"][0]
                    self._respond(
                        200,
                        b"<html><body><h2>Authentication successful!</h2>"
                        b"<p>You can close this tab and return to the terminal.</p>"
                        b"</body></html>",
                    )
                elif "error" in params:
                    manager._auth_error = params["error"][0]
                    self._respond(
                        400,
                        b"<html><body><h2>Authentication failed.</h2>"
                        b"<p>Check the terminal for details.</p></body></html>",
                    )
                else:
                    self._respond(400, b"Missing code or error parameter")

            def _respond(self, code: int, body: bytes) -> None:
                self.send_response(code)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, fmt, *args):  # suppress access logs
                pass

        return _Handler
