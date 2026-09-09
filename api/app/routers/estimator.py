"""
estimator.py — public API for the Savings Estimator landing-page feature.
No authentication required (this runs before a user has an account); see
estimator_service.py for the full, documented methodology.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.estimator_service import estimate_savings

router = APIRouter(prefix="/estimate", tags=["estimate"])


class EstimateRequest(BaseModel):
    address: str = Field(..., min_length=3, max_length=200)


@router.post("/savings")
def get_savings_estimate(payload: EstimateRequest):
    return estimate_savings(payload.address)
