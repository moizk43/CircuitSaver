"""
security.py — Supabase JWT verification for protected FastAPI routes.

Closes a gap found during audit: authFetch() sends
`Authorization: Bearer <supabase_access_token>`, but no route previously
validated that token server-side. get_current_user() verifies the token
against Supabase Auth directly (no local secret handling required) and
returns the authenticated user's id/email. require_admin() builds on top
of it to gate destructive/admin-only actions.
"""

import os
from fastapi import Header, HTTPException, Depends
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Mirrors web/js/auth.js ADMIN_EMAILS — kept in one place server-side so
# admin-only actions can no longer be triggered by a direct API call from a
# non-admin session, which was previously possible.
ADMIN_EMAILS = {"moizkothawala@gmail.com"}


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")
    token = authorization.split(" ", 1)[1]
    try:
        user_response = _supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    user = getattr(user_response, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")
    return {"id": user.id, "email": user.email}


def require_admin(user: dict = Depends(get_current_user)):
    if (user.get("email") or "").lower() not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user
