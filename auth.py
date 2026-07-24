"""
Auth guard — the reusable dependency that protects routes.

One function stands at every locked door: it extracts the Bearer token,
asks Supabase whether it's real, and either injects the user or returns 401.
Applied to more than one route (profile + dashboard) so the guard is proven reusable.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import supabase_client

# HTTPBearer makes the Swagger "Authorize" padlock appear on protected routes.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    # Stage 2: a token must be presented at all.
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})

    token = credentials.credentials

    if not supabase_client.is_configured():
        raise HTTPException(
            status_code=503,
            detail={"error": "Auth backend not configured (set SUPABASE_URL / SUPABASE_KEY)"},
        )

    # Stage 3: verify the token with Supabase (a real network call, so it's trustworthy).
    try:
        client = supabase_client.get_client()
        response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})

    return {
        "id": user.id,
        "email": user.email,
        "created_at": getattr(user, "created_at", None),
    }
