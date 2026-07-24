# AI rematch — prompt v2 (improved)

Build a secure FastAPI API with Supabase Auth. Hard rules:

1. Five routes: POST /auth/signup, POST /auth/login, POST /auth/logout, GET /protected/profile, GET /public/info.
2. Status codes: 201 signup, 200 login/read, 204 logout, 400 missing email/password, 401 on missing/malformed/invalid/expired token. Every error body is top-level `{"error": "..."}` (never FastAPI's `detail`).
3. The auth check MUST be a single reusable dependency applied to MORE THAN ONE route (profile + logout + a dashboard), not copy-pasted.
4. Token extraction MUST correctly handle the `Authorization: Bearer <token>` format — reject `Authorization: <token>` (no Bearer) and a missing header, both with 401, without crashing.
5. Verify the token by calling `supabase.auth.get_user(token)` and CHECK the result — treat a missing/None user as 401. Never trust the call blindly.
6. Read `SUPABASE_URL` and the **anon** key from `.env` (git-ignored); commit `.env.example`. Never use the service_role key; never log the token.
7. Add FastAPI `HTTPBearer` so Swagger `/docs` shows the Authorize padlock on protected routes.

Quarantine under ai-version/.
