"""
swarm.py
FastAPI router exposing the Swarm Architect pipeline:
- POST /swarm/shed-event: runs Capacity Allocator for a transformer
- POST /swarm/restart-plan: runs Anti-Rebound Classifier for restarting households
"""

#Wire the Ledger Into Your Existing Swarm Router
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database import get_db
from app.db.models import ShedLedgerEntry, GridSignalLog

#Web Socket Thing
from app.websocket.connection_manager import manager


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.optimizer.swarm_engine import allocate_capacity, load_transformers
from app.services.optimizer.anti_rebound import predict_stagger, STAGGER_DELAY_MINUTES

router = APIRouter(prefix="/swarm", tags=["swarm"])


class ShedEventRequest(BaseModel):
    transformer_id: str = Field(..., example="XFMR_AUS_001")
    shed_target_kw: float = Field(..., gt=0, example=5.0)
    current_co2_lbs_per_kwh: Optional[float] = Field(default=0.85)
    peak_rate_usd_per_kwh: Optional[float] = Field(default=0.15)


class HouseholdAllocation(BaseModel):
    user_id: str
    household_type: str
    region: str
    allocated_kw: float
    shiftable_capacity_kwh: float
    priority_score: float
    recommended_appliance: Optional[str]
    estimated_carbon_saved_lbs: float
    estimated_cost_saved_usd: float
    is_capped: bool


class ShedEventResponse(BaseModel):
    transformer_id: str
    shed_target_kw: float
    total_allocated_kw: float
    shortfall_kw: float
    households_involved: int
    total_carbon_saved_lbs: float
    total_cost_saved_usd: float
    transformer_rated_kva: float
    transformer_status_before: str
    allocations: List[HouseholdAllocation]


class RestartHousehold(BaseModel):
    user_id: str
    appliance: str
    appliance_kw: float
    transformer_rated_kva: float
    transformer_loading_percent: float
    num_simultaneous_restarts: int
    flexibility_score: float
    carbon_priority_weight: float
    cost_priority_weight: float


class RestartPlanRequest(BaseModel):
    households: List[RestartHousehold]


class RestartPlanEntry(BaseModel):
    user_id: str
    appliance: str
    stagger_label: str
    recommended_delay_minutes: int
    confidence: float


class RestartPlanResponse(BaseModel):
    schedule: List[RestartPlanEntry]

@router.post("/shed-event", response_model=ShedEventResponse)
async def trigger_shed_event(request: ShedEventRequest, db: Session = Depends(get_db)):
    try:
        summary, result_df = allocate_capacity(
            transformer_id=request.transformer_id,
            shed_target_kw=request.shed_target_kw,
            current_co2_lbs_per_kwh=request.current_co2_lbs_per_kwh,
            peak_rate_usd_per_kwh=request.peak_rate_usd_per_kwh,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    allocations = result_df.to_dict(orient="records")

    grid_log = GridSignalLog(
        transformer_id=request.transformer_id,
        grid_region="ERCOT",
        co2_moer=request.current_co2_lbs_per_kwh,
        transformer_loading_percent=None,
        event_type="shed_event",
    )
    db.add(grid_log)

    for row in allocations:
        ledger_entry = ShedLedgerEntry(
            transformer_id=request.transformer_id,
            user_id=row["user_id"],
            household_type=row["household_type"],
            region=row["region"],
            shed_target_kw=request.shed_target_kw,
            allocated_kw=row["allocated_kw"],
            shiftable_capacity_kwh=row["shiftable_capacity_kwh"],
            priority_score=row["priority_score"],
            recommended_appliance=row["recommended_appliance"],
            estimated_carbon_saved_lbs=row["estimated_carbon_saved_lbs"],
            estimated_cost_saved_usd=row["estimated_cost_saved_usd"],
            is_capped=row["is_capped"],
            shortfall_kw=summary["shortfall_kw"],
            transformer_status_before=summary["transformer_status_before"],
        )
        db.add(ledger_entry)

    db.commit()

    broadcast_payload = {
        "event_type": "shed_event",
        **summary,
        "allocations": allocations,
    }
    await manager.broadcast(broadcast_payload)

    return ShedEventResponse(
        **summary,
        allocations=allocations,
    )

@router.post("/restart-plan", response_model=RestartPlanResponse)
async def trigger_restart_plan(request: RestartPlanRequest):
    if not request.households:
        raise HTTPException(status_code=400, detail="No households provided for restart planning.")

    schedule = []
    for household in request.households:
        features = {
            "appliance_kw": household.appliance_kw,
            "transformer_rated_kva": household.transformer_rated_kva,
            "transformer_loading_percent": household.transformer_loading_percent,
            "num_simultaneous_restarts": household.num_simultaneous_restarts,
            "flexibility_score": household.flexibility_score,
            "carbon_priority_weight": household.carbon_priority_weight,
            "cost_priority_weight": household.cost_priority_weight,
        }
        try:
            prediction = predict_stagger(features)
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))

        schedule.append(RestartPlanEntry(
            user_id=household.user_id,
            appliance=household.appliance,
            stagger_label=prediction["stagger_label"],
            recommended_delay_minutes=prediction["recommended_delay_minutes"],
            confidence=prediction["confidence"],
        ))

    schedule = sorted(schedule, key=lambda x: x.recommended_delay_minutes)

    broadcast_payload = {
        "event_type": "restart_plan",
        "schedule": [entry.dict() for entry in schedule],
    }
    await manager.broadcast(broadcast_payload)

    return RestartPlanResponse(schedule=schedule)


@router.get("/transformers")
def list_transformers():
    transformers = load_transformers()
    return transformers.to_dict(orient="records")

@router.get("/ledger")
def get_ledger_history(db: Session = Depends(get_db), limit: int = 50):
    entries = db.query(ShedLedgerEntry).order_by(ShedLedgerEntry.created_at.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "transformer_id": e.transformer_id,
            "user_id": e.user_id,
            "household_type": e.household_type,
            "region": e.region,
            "allocated_kw": e.allocated_kw,
            "estimated_carbon_saved_lbs": e.estimated_carbon_saved_lbs,
            "estimated_cost_saved_usd": e.estimated_cost_saved_usd,
            "created_at": e.created_at,
        }
        for e in entries
    ]