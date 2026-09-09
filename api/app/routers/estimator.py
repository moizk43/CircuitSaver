"""
estimator.py — public API for the Savings Estimator: address autocomplete
(proxying Nominatim) and the savings estimate itself (now geocoding- and
weather-aware; see estimator_service.py for full methodology).
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.estimator_service import estimate_savings
from app.services.geocoding_service import autocomplete_address

router = APIRouter(prefix="/estimate", tags=["estimate"])


class EstimateRequest(BaseModel):
    address: str = Field(..., min_length=3, max_length=200)


@router.get("/autocomplete")
def get_address_suggestions(q: str):
    return {"results": autocomplete_address(q)}


@router.post("/savings")
def get_savings_estimate(payload: EstimateRequest):
    return estimate_savings(payload.address)
