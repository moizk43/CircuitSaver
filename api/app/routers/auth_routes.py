import os
from fastapi import FastAPI, HTTPException, APIRouter
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
        raise HTTPException(400, str(e))
    if result.user is None:
        raise HTTPException(400, "Could not create account. Try a different email.")
    return {"email": payload.email, "user_id": result.user.id}

@router.post("/signin")
def signin(payload: SignInRequest):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception:
        raise HTTPException(401, "Incorrect email or password.")
    return {
        "email": payload.email,
        "access_token": result.session.access_token,
    }