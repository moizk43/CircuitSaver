"""
profile.py — household profile storage, linking a Supabase-authenticated
user to a self-reported address/region and their savings-estimator result.

Backed by the `household_profiles` table (RLS-protected: a user can only
ever see or modify their own row via auth.uid() = user_id policies).
"""

import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import create_client

from app.core.security import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class HouseholdProfileIn(BaseModel):
    address_text: str
    region: str
    estimated_avg_load_kw: Optional[float] = None
    estimated_annual_savings_low_usd: Optional[float] = None
    estimated_annual_savings_high_usd: Optional[float] = None
    estimated_co2_reduction_kg_per_year: Optional[float] = None


@router.get("/household")
def get_household_profile(user: dict = Depends(get_current_user)):
    result = (
        _supabase.table("household_profiles")
        .select("*")
        .eq("user_id", user["id"])
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if not rows:
        return {"exists": False}
    return {"exists": True, "profile": rows[0]}


@router.post("/household")
def save_household_profile(payload: HouseholdProfileIn, user: dict = Depends(get_current_user)):
    row = payload.dict()
    row["user_id"] = user["id"]
    row["email"] = user["email"]
    row["onboarding_completed"] = True
    try:
        result = (
            _supabase.table("household_profiles")
            .upsert(row, on_conflict="user_id")
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save household profile: {exc}")
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save household profile.")
    return {"exists": True, "profile": result.data[0]}
