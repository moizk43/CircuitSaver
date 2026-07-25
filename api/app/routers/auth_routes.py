import os
from fastapi import HTTPException, APIRouter, Header
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

router = APIRouter(prefix="/api", tags=["auth"])

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(payload: SignUpRequest):
    if len(payload.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")

    try:
        result = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception as e:
        msg = str(e).lower()
        if "already" in msg or "registered" in msg or "exists" in msg:
            raise HTTPException(409, "An account with this email already exists.")
        raise HTTPException(400, str(e))

    if result.user is None:
        raise HTTPException(400, "Could not create account. Try a different email.")

    # Supabase Auth anti-enumeration behavior: existing accounts return a
    # user object with an empty identities list instead of raising an error.
    if not result.user.identities:
        raise HTTPException(409, "An account with this email already exists.")

    if result.session is None:
        return {
            "email": payload.email,
            "user_id": result.user.id,
            "needs_confirmation": True,
        }

    return {
        "email": payload.email,
        "user_id": result.user.id,
        "access_token": result.session.access_token,
        "needs_confirmation": False,
    }

@router.post("/signin")
def signin(payload: SignInRequest):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception:
        raise HTTPException(401, "Incorrect email or password.")

    if result.session is None:
        raise HTTPException(401, "Incorrect email or password.")

    return {
        "email": payload.email,
        "access_token": result.session.access_token,
    }

@router.get("/me")
def me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated.")

    token = authorization.split(" ")[1]

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(401, "Session expired. Please sign in again.")

    if result is None or result.user is None:
        raise HTTPException(401, "Session expired. Please sign in again.")

    return {"email": result.user.email}