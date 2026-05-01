"""Gmail service factory — bridges TokenStore to the Gmail API.

Given a user_id (Gmail address), returns a googleapiclient Resource for
Gmail v1, ready to make API calls. Raises :class:`GmailAuthError` if
the user has no usable credentials.

The factory caches one service per user_id. The underlying
:class:`google.oauth2.credentials.Credentials` object refreshes itself
in-place when its access token expires, so cached services stay valid
across token refreshes.
"""

from __future__ import annotations

from functools import lru_cache

from googleapiclient.discovery import Resource, build

from agenticfiller.auth import TokenStore


class GmailAuthError(LookupError):
    """Raised when a user has no usable Gmail credentials.

    Subclass of :class:`LookupError` so callers can catch it with the
    builtin if they don't want to import this module.
    """


# Module-level singleton: avoids re-creating the token directory on
# every call and lets us swap in a fake store for tests.
_token_store = TokenStore()


def get_gmail_service(user_id: str) -> Resource:
    """Return a Gmail v1 service for *user_id*.

    Args:
        user_id: The Gmail address of an authenticated user
            (e.g. "alice@gmail.com").

    Returns:
        A ``googleapiclient.discovery.Resource`` for the Gmail v1 API.
        Call methods on it like::

            service.users().messages().list(userId="me", q="...").execute()

    Raises:
        GmailAuthError: When *user_id* has no token on disk, or the
            stored token cannot be refreshed. The error message
            includes the exact CLI command to fix it.
    """
    creds = _token_store.load(user_id)
    if creds is None:
        raise GmailAuthError(
            f"No usable credentials for {user_id!r}. "
            f"Run: uv run agenticfiller-auth --user {user_id}"
        )
    return _build_service(user_id, creds_id=id(creds))


@lru_cache(maxsize=128)
def _build_service(user_id: str, creds_id: int) -> Resource:
    """Cached service builder.

    Cache key is (user_id, creds_id). ``creds_id`` ensures that if a
    user re-authenticates and gets a brand-new ``Credentials`` object,
    we don't keep handing back a service bound to the old one.
    """
    creds = _token_store.load(user_id)
    # cache_discovery=False suppresses a deprecation warning that
    # appears when google-api-python-client tries to write its
    # discovery document cache to disk on Python 3.13+.
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def clear_service_cache() -> None:
    """Drop the cached service objects. Mostly for tests."""
    _build_service.cache_clear()
