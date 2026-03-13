"""Validation API endpoints"""
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.db.models import Claim, Validation, ClaimStatus, ValidationSource
from app.models.claim_models import ClaimInput
from app.models.validation_models import ValidationResult
from app.services.validation.engine import run_validation

router = APIRouter(prefix="/claims", tags=["validation"])


@router.post("/{claim_id}/validate/deterministic", response_model=ValidationResult)
def validate_claim_deterministic(
    claim_id: UUID,
    session: Session = Depends(get_session)
):
    """
    Run deterministic validation on a claim.
    
    - Load claim
    - Run validation engine
    - Store ValidationResult in DB
    - Update claim status:
        - PASS → READY_FOR_AI
        - FAIL → NEEDS_FIXES
    - Return ValidationResult
    """
    # Log validation started
    print(json.dumps({
        "event": "validation_started",
        "claim_id": str(claim_id),
        "source": "deterministic"
    }))
    
    try:
        # Load claim
        statement = select(Claim).where(Claim.id == claim_id)
        claim = session.exec(statement).first()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Parse claim JSON into ClaimInput
        try:
            claim_input = ClaimInput(**claim.raw_claim_json)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid claim data: {str(e)}"
            )
        
        # Run validation engine
        result = run_validation(claim_input)
        
        # Store validation result in DB
        validation = Validation(
            claim_id=claim_id,
            source=ValidationSource.deterministic,
            result_json=result.model_dump(mode="json")
        )
        session.add(validation)
        
        # Update claim status
        if result.status == "PASS":
            claim.status = ClaimStatus.READY_FOR_AI
        else:
            claim.status = ClaimStatus.NEEDS_FIXES
        
        session.commit()
        session.refresh(validation)
        
        # Log validation completed
        print(json.dumps({
            "event": "validation_completed",
            "claim_id": str(claim_id),
            "validation_source": "deterministic",
            "num_issues": len(result.issues),
            "status": result.status
        }))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        # Log validation failed
        print(json.dumps({
            "event": "validation_failed",
            "claim_id": str(claim_id),
            "error": str(e)
        }))
        raise HTTPException(status_code=500, detail=str(e))
