"""
FlyRank W2 · A4 — Auth · Login & protect.

Supabase is the Identity Provider: it stores accounts, hashes passwords, and
signs JWTs. This backend's job is the part that matters — receive a token,
verify it, and open or refuse the door. We never hash a password ourselves.

Routes:
    POST /auth/signup        create account            (no auth)   201/400
    POST /auth/login         authenticate -> JWT       (no auth)   200/400/401
    POST /auth/logout        end session               (bearer)    204
    GET  /protected/profile  private profile           (bearer)    200/401
    GET  /protected/dashboard second guarded route     (bearer)    200/401
    GET  /public/info        open data                 (no auth)   200
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi import Request
from pydantic import BaseModel

import supabase_client
from auth import bearer_scheme, get_current_user

app = FastAPI(
    title="Auth API",
    version="1.0.0",
    description=(
        "Secure API using **Supabase Auth**. Sign up, log in, log out, and guard "
        "routes behind a verified JWT. Click **Authorize** and paste an access token "
        "to try the protected endpoints."
    ),
)


# Normalize validation and HTTPException bodies to a top-level {"error": ...}.
@app.exception_handler(RequestValidationError)
async def _validation_handler(_: Request, __: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "email and password are required"})


@app.exception_handler(HTTPException)
async def _http_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


class Credentials(BaseModel):
    email: str
    password: str


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "Auth API",
        "identity_provider": "supabase",
        "configured": supabase_client.is_configured(),
        "routes": [
            "/auth/signup", "/auth/login", "/auth/logout",
            "/protected/profile", "/protected/dashboard", "/public/info",
        ],
    }


@app.get("/public/info", tags=["public"], summary="Open data (no auth)")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=201, tags=["auth"], summary="Create an account")
def signup(body: Credentials):
    if not body.email.strip() or not body.password.strip():
        return JSONResponse(status_code=400, content={"error": "email and password are required"})
    try:
        client = supabase_client.get_client()
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"error": str(exc)})
    try:
        result = client.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    user = getattr(result, "user", None)
    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "message": "Account created",
    }


@app.post("/auth/login", tags=["auth"], summary="Authenticate and receive a JWT")
def login(body: Credentials):
    if not body.email.strip() or not body.password.strip():
        return JSONResponse(status_code=400, content={"error": "email and password are required"})
    try:
        client = supabase_client.get_client()
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"error": str(exc)})
    try:
        result = client.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

    session = getattr(result, "session", None)
    if session is None:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/logout", status_code=204, tags=["auth"],
          summary="End session (protected)", dependencies=[Depends(get_current_user)])
def logout():
    try:
        supabase_client.get_client().auth.sign_out()
    except Exception:
        pass  # logout is best-effort; the token expires regardless
    return Response(status_code=204)


@app.get("/protected/profile", tags=["protected"], summary="Private profile (bearer)")
def profile(user: dict = Depends(get_current_user)):
    return {"user": user}


@app.get("/protected/dashboard", tags=["protected"],
         summary="Second guarded route — same guard, zero new auth code (bearer)")
def dashboard(user: dict = Depends(get_current_user)):
    return {"message": f"Welcome back, {user['email']}", "widgets": ["audits", "reports"]}
