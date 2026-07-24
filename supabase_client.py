"""
Supabase client — created once from environment variables.

We never hardcode keys. The anon (public) key is what belongs in an app;
the service_role key would bypass all security and must never be used here.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def is_configured() -> bool:
    return (
        SUPABASE_URL.startswith("https://")
        and "your-project-ref" not in SUPABASE_URL
        and bool(SUPABASE_KEY)
        and SUPABASE_KEY != "your-anon-public-key"
    )


_client = None


def get_client():
    """Lazily build the Supabase client so the app can start without real keys."""
    global _client
    if not is_configured():
        raise RuntimeError(
            "Supabase is not configured. Copy .env.example to .env and set "
            "SUPABASE_URL and SUPABASE_KEY from your project's API settings."
        )
    if _client is None:
        from supabase import create_client

        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
