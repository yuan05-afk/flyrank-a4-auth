"""
AI rematch v1 — quarantined. Contains the classic auth mistakes a review must catch.
NOT the submission.
"""

import os

from fastapi import FastAPI, Request
from supabase import create_client

app = FastAPI()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


@app.get("/public/info")
def public():
    return {"message": "public"}


@app.post("/auth/signup")
def signup(body: dict):
    # MISTAKE: no validation — missing email/password will raise, not return 400
    return supabase.auth.sign_up({"email": body["email"], "password": body["password"]})


@app.post("/auth/login")
def login(body: dict):
    res = supabase.auth.sign_in_with_password(
        {"email": body["email"], "password": body["password"]}
    )
    return {"access_token": res.session.access_token}


@app.get("/protected/profile")
def profile(request: Request):
    # MISTAKE 1: reads the raw header and does NOT strip the "Bearer " prefix,
    #            so it passes "Bearer eyJ..." as the token -> verification fails,
    #            and "Authorization: eyJ..." (no Bearer) would "work" inconsistently.
    token = request.headers.get("Authorization")
    if not token:
        return {"error": "no token"}  # MISTAKE 2: returns 200, not 401

    # MISTAKE 3: trusts get_user without checking whether user is None
    user = supabase.auth.get_user(token)
    return {"user": user}

    # MISTAKE 4: no reusable dependency — this check can't be shared with other routes
    # MISTAKE 5: no logout route
