"""
AI rematch v2 — quarantined. Reusable dependency, correct Bearer parsing,
checks the get_user result. Closer to the hand-built version.
"""

import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client

app = FastAPI(title="Auth API")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
bearer = HTTPBearer(auto_error=False)


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail={"error": "Access token required"})
    try:
        res = supabase.auth.get_user(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})
    if getattr(res, "user", None) is None:
        raise HTTPException(status_code=401, detail={"error": "Invalid or expired token"})
    return {"id": res.user.id, "email": res.user.email}


@app.get("/public/info")
def public():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=201)
def signup(body: dict):
    if not body.get("email") or not body.get("password"):
        return JSONResponse(status_code=400, content={"error": "email and password are required"})
    res = supabase.auth.sign_up({"email": body["email"], "password": body["password"]})
    return {"id": res.user.id, "email": res.user.email}


@app.post("/auth/login")
def login(body: dict):
    if not body.get("email") or not body.get("password"):
        return JSONResponse(status_code=400, content={"error": "email and password are required"})
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": body["email"], "password": body["password"]}
        )
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})
    return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}


@app.post("/auth/logout", status_code=204, dependencies=[Depends(current_user)])
def logout():
    supabase.auth.sign_out()
    return Response(status_code=204)


@app.get("/protected/profile")
def profile(user: dict = Depends(current_user)):
    return {"user": user}


@app.get("/protected/dashboard")
def dashboard(user: dict = Depends(current_user)):
    return {"message": f"Welcome back, {user['email']}"}
