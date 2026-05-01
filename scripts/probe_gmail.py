"""Probe the Gmail service factory end-to-end.

Usage::

    uv run python scripts/probe_gmail.py --user alice@gmail.com

Builds a Gmail service for *--user*, lists their labels, and prints the
first 10. A successful run proves that:

  1. Credentials are on disk and loadable.
  2. The service factory wires them into a googleapiclient Resource.
  3. The Gmail API accepts the credentials and answers a real call.

If you see a "✅ Found N labels" message, Step 3 is working and you
can move on to Step 4 (Gmail operations).
"""

from __future__ import annotations

import argparse
import sys

from agenticfiller.gmail.client import GmailAuthError, get_gmail_service


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--user",
        required=True,
        help="Gmail address of an authenticated user.",
    )
    args = parser.parse_args()

    # 1. Build the service.
    try:
        service = get_gmail_service(args.user)
    except GmailAuthError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    print(f"✅ Built Gmail service for {args.user}")

    # 2. Make a small, low-quota call to prove the credentials work.
    #    labels.list returns instantly and counts toward quota minimally.
    try:
        result = service.users().labels().list(userId="me").execute()
    except Exception as e:  # noqa: BLE001 — surface anything to the user
        print(f"❌ Gmail API call failed: {e}", file=sys.stderr)
        return 2

    labels = result.get("labels", [])
    print(f"📬 Found {len(labels)} labels. First 10:")
    for label in labels[:10]:
        # 'system' = Gmail-defined (INBOX, SENT, etc.)
        # 'user'   = labels you created yourself
        kind = label.get("type", "?")
        print(f"   [{kind:6}] {label['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
