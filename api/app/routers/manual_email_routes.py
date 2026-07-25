from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
from app.services.notifications.email_service import (
    send_email_notification,
    build_manual_shed_summary_html,
    build_manual_shed_appliance_html,
)

router = APIRouter()

class ApplianceEntry(BaseModel):
    order: int
    id: str
    label: str
    kwh: float
    estimated_carbon_saved_lbs: float
    estimated_cost_saved_usd: float

class TotalsEntry(BaseModel):
    estimated_kwh_shed: float
    estimated_carbon_saved_lbs: float
    estimated_cost_saved_usd: float

class ManualSummaryRequest(BaseModel):
    email: EmailStr
    appliances: List[ApplianceEntry]
    totals: TotalsEntry

class ManualApplianceRequest(BaseModel):
    email: EmailStr
    appliance: ApplianceEntry

@router.post("/api/manual-shed-email/summary")
async def send_manual_summary(req: ManualSummaryRequest):
    try:
        html_body = build_manual_shed_summary_html(
            [a.model_dump() for a in req.appliances],
            req.totals.model_dump(),
        )
        send_email_notification(
            to_address=req.email,
            subject="CircuitSaver Manual Shed Summary",
            html_body=html_body,
        )
        return {"ok": True, "message": "Summary email sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send summary email: {str(e)}")

@router.post("/api/manual-shed-email/appliance")
async def send_manual_appliance(req: ManualApplianceRequest):
    try:
        html_body = build_manual_shed_appliance_html(req.appliance.model_dump())
        send_email_notification(
            to_address=req.email,
            subject=f"CircuitSaver Appliance Recommendation: {req.appliance.label}",
            html_body=html_body,
        )
        return {"ok": True, "message": "Appliance email sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send appliance email: {str(e)}")