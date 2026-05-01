"""Gmail service factory — bridges TokenStore to the Gmail API.

Filled in during Step 3.
"""

from __future__ import annotations

# from googleapiclient.discovery import build
# from agenticfiller.auth import TokenStore


def get_gmail_service(user_id: str):  # type: ignore[no-untyped-def]
    """Return a googleapiclient Gmail v1 service for *user_id*.

    Raises:
        LookupError: if the user is not yet authenticated.

    To be implemented in Step 3.
    """
    raise NotImplementedError("Implemented in Step 3.")
