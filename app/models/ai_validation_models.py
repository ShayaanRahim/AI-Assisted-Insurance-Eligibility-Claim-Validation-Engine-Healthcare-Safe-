"""
Pydantic models for AI validation output.
These enforce strict schema compliance on LLM responses.
"""
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class AIValidationIssue(BaseModel):
    """
    Represents a single issue detected by AI validation.
    Must not include hallucinated fields.
    """
    type: Literal["missing_field", "inconsistency", "coverage_risk"]
    field: str = Field(description="Field name in dot notation (e.g., 'coverage.policy_id')")
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(description="Human-readable explanation of the issue")


class AIValidationResult(BaseModel):
    """
    Complete AI validation result.
    This is the ONLY valid output format for AI validation.
    
    Important:
    - "unknown" is a valid status when AI cannot determine outcome
    - confidence must be between 0.0 and 1.0
    - Low confidence should force needs_human_review = true
    """
    status: Literal["approved", "needs_review", "rejected", "unknown"]
    issues: List[AIValidationIssue] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, description="AI confidence in this assessment")
    needs_human_review: bool
    rationale: str = Field(description="Explanation of the decision")
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class AIValidationRequest(BaseModel):
    """
    Internal model for structuring data sent to AI validation.
    Not exposed in API.
    """
    claim_data: dict
    deterministic_result: dict
    
    
# Safe fallback when AI fails
SAFE_FALLBACK_RESPONSE = AIValidationResult(
    status="needs_review",
    issues=[],
    confidence=0.0,
    needs_human_review=True,
    rationale="AI validation unavailable; requires manual review."
)
