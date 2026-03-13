"""Pydantic models for claim input and responses"""
from datetime import date
from typing import List
from pydantic import BaseModel, Field


class Patient(BaseModel):
    id: str
    date_of_birth: date


class Coverage(BaseModel):
    policy_id: str
    start_date: date
    end_date: date


class CareEvent(BaseModel):
    service_date: date
    location: str


class Billing(BaseModel):
    codes: List[str]


class ClaimInput(BaseModel):
    """Input schema for creating a claim"""
    patient: Patient
    coverage: Coverage
    care_event: CareEvent
    billing: Billing


class ClaimResponse(BaseModel):
    """Response schema for claim"""
    claim_id: str
    status: str
    created_at: str
    updated_at: str
    raw_claim: dict
