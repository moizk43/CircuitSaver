"""
models.py
SQLAlchemy ORM models for baseline predictions, the shed event ledger,
and grid signal logs.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class BaselinePrediction(Base):
    __tablename__ = "baseline_predictions"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(String, index=True)
    user_id = Column(String, index=True)
    region = Column(String)
    predicted_load_kw = Column(Float)
    temperature_c = Column(Float)
    hour = Column(Integer)
    day_of_week = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShedLedgerEntry(Base):
    __tablename__ = "shed_ledger"

    id = Column(Integer, primary_key=True, index=True)
    transformer_id = Column(String, index=True)
    user_id = Column(String, index=True)
    household_type = Column(String)
    region = Column(String)
    shed_target_kw = Column(Float)
    allocated_kw = Column(Float)
    shiftable_capacity_kwh = Column(Float)
    priority_score = Column(Float)
    recommended_appliance = Column(String, nullable=True)
    estimated_carbon_saved_lbs = Column(Float)
    estimated_cost_saved_usd = Column(Float)
    is_capped = Column(Boolean)
    shortfall_kw = Column(Float)
    transformer_status_before = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GridSignalLog(Base):
    __tablename__ = "grid_signal_log"

    id = Column(Integer, primary_key=True, index=True)
    transformer_id = Column(String, index=True, nullable=True)
    grid_region = Column(String)
    co2_moer = Column(Float, nullable=True)
    transformer_loading_percent = Column(Float, nullable=True)
    event_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())