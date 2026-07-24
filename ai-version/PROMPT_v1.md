# AI rematch — prompt v1 (from memory)

Build a FastAPI API that uses Supabase for authentication.

- POST /auth/signup (email, password) -> create user
- POST /auth/login -> return the access token
- POST /auth/logout -> end session
- GET /protected/profile -> only for logged-in users
- GET /public/info -> open to everyone

Use the Supabase Python SDK. Read the keys from environment variables.
Protect the profile route by checking the Authorization header.
