"""CLI: authenticate one Gmail user.

Run via the console script registered in pyproject.toml::

    agenticfiller-auth --user alice@gmail.com

Or directly::

    python -m agenticfiller.cli.authenticate --user alice@gmail.com
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from agenticfiller.auth import OAuthManager


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Authenticate a Gmail user and persist their tokens."
    )
    parser.add_argument(
        "--user",
        required=True,
        help="Gmail address to authenticate (e.g. alice@gmail.com)",
    )
    args = parser.parse_args()

    try:
        client_id = os.environ["GOOGLE_CLIENT_ID"]
        client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
    except KeyError as e:
        print(f"❌ Missing env var: {e.args[0]}", file=sys.stderr)
        print("   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env", file=sys.stderr)
        return 1

    manager = OAuthManager(client_id, client_secret)

    if manager.store.is_authenticated(args.user):
        print(f"✅ {args.user} is already authenticated.")
        return 0

    print(f"🔐 Starting OAuth flow for {args.user}...")
    manager.run_auth_flow(args.user)
    print(f"✅ Authenticated! Token saved for {args.user}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
