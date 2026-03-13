"""Pydantic models for validation results"""
from typing import List, Literal
from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """Represents a single validation issue"""
    code: str = Field(description="Stable string code, e.g. MISSING_POLICY_ID")
    severity: Literal["ERROR", "WARNING"]
    field: str = Field(description="Dot-notation string indicating the field")
    message: str = Field(description="Human readable message")


class ValidationResult(BaseModel):
    """Complete validation result"""
    status: Literal["PASS", "FAIL"]
    issues: List[ValidationIssue]
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool
    rationale: str
