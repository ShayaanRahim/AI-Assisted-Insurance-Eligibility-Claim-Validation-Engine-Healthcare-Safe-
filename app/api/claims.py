"""Claims API endpoints"""
import json
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Claim, Validation, ClaimStatus
from app.models.claim_models import ClaimInput, ClaimResponse

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", response_model=dict, status_code=201)
def create_claim(
    claim_input: ClaimInput,
    session: Session = Depends(get_session)
):
    """
    Create a new claim.
    
    - Validates request with Pydantic
    - Stores raw claim JSON
    - Sets status = DRAFT
    - Returns claim_id
    """
    # Log event
    print(json.dumps({
        "event": "claim_created",
        "timestamp": str(claim_input)
    }))
    
    # Create claim
    claim = Claim(
        raw_claim_json=claim_input.model_dump(mode="json"),
        status=ClaimStatus.DRAFT
    )
    
    session.add(claim)
    session.commit()
    session.refresh(claim)
    
    return {"claim_id": str(claim.id)}


@router.get("/{claim_id}")
def get_claim(
    claim_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Get claim by ID.
    
    Returns:
    - claim metadata
    - raw claim
    - all validations (ordered by time)
    """
    # Get claim
    statement = select(Claim).where(Claim.id == claim_id)
    claim = session.exec(statement).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Get all validations for this claim
    validations_statement = select(Validation).where(
        Validation.claim_id == claim_id
    ).order_by(Validation.created_at)
    validations = session.exec(validations_statement).all()
    
    return {
        "claim_id": str(claim.id),
        "status": claim.status,
        "created_at": claim.created_at.isoformat(),
        "updated_at": claim.updated_at.isoformat(),
        "raw_claim": claim.raw_claim_json,
        "validations": [
            {
                "validation_id": str(v.id),
                "source": v.source,
                "result": v.result_json,
                "created_at": v.created_at.isoformat()
            }
            for v in validations
        ]
    }
