"""
Tests for AI validation models and schema enforcement.
"""
import pytest
from pydantic import ValidationError
from app.models.ai_validation_models import (
    AIValidationResult,
    AIValidationIssue,
    SAFE_FALLBACK_RESPONSE
)


def test_valid_ai_result():
    """Valid AI result should pass validation"""
    result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.95,
        needs_human_review=False,
        rationale="All checks pass"
    )
    
    assert result.status == "approved"
    assert result.confidence == 0.95


def test_ai_result_with_issues():
    """AI result with issues should validate correctly"""
    result = AIValidationResult(
        status="needs_review",
        issues=[
            AIValidationIssue(
                type="coverage_risk",
                field="coverage.end_date",
                severity="medium",
                explanation="Coverage expires soon"
            )
        ],
        confidence=0.7,
        needs_human_review=True,
        rationale="Potential coverage issue"
    )
    
    assert len(result.issues) == 1
    assert result.issues[0].type == "coverage_risk"


def test_confidence_must_be_in_range():
    """Confidence must be between 0 and 1"""
    # Too high
    with pytest.raises(ValidationError):
        AIValidationResult(
            status="approved",
            issues=[],
            confidence=1.5,
            needs_human_review=False,
            rationale="Test"
        )
    
    # Too low
    with pytest.raises(ValidationError):
        AIValidationResult(
            status="approved",
            issues=[],
            confidence=-0.1,
            needs_human_review=False,
            rationale="Test"
        )


def test_invalid_status_rejected():
    """Invalid status values should be rejected"""
    with pytest.raises(ValidationError):
        AIValidationResult(
            status="maybe",  # Invalid status
            issues=[],
            confidence=0.8,
            needs_human_review=False,
            rationale="Test"
        )


def test_invalid_issue_type_rejected():
    """Invalid issue type should be rejected"""
    with pytest.raises(ValidationError):
        AIValidationIssue(
            type="random_type",  # Invalid type
            field="some.field",
            severity="low",
            explanation="Test"
        )


def test_invalid_severity_rejected():
    """Invalid severity should be rejected"""
    with pytest.raises(ValidationError):
        AIValidationIssue(
            type="inconsistency",
            field="some.field",
            severity="critical",  # Invalid severity
            explanation="Test"
        )


def test_unknown_status_is_valid():
    """'unknown' should be a valid status"""
    result = AIValidationResult(
        status="unknown",
        issues=[],
        confidence=0.5,
        needs_human_review=True,
        rationale="Insufficient information"
    )
    
    assert result.status == "unknown"


def test_safe_fallback_response():
    """Safe fallback response should be valid"""
    assert SAFE_FALLBACK_RESPONSE.status == "needs_review"
    assert SAFE_FALLBACK_RESPONSE.confidence == 0.0
    assert SAFE_FALLBACK_RESPONSE.needs_human_review is True
    assert len(SAFE_FALLBACK_RESPONSE.issues) == 0


def test_ai_result_serialization():
    """AI result should serialize to dict correctly"""
    result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.9,
        needs_human_review=False,
        rationale="Test"
    )
    
    data = result.model_dump()
    
    assert data["status"] == "approved"
    assert data["confidence"] == 0.9
    assert isinstance(data["issues"], list)


def test_ai_result_from_json():
    """AI result should be constructable from JSON"""
    data = {
        "status": "needs_review",
        "issues": [
            {
                "type": "missing_field",
                "field": "patient.id",
                "severity": "high",
                "explanation": "Patient ID is missing"
            }
        ],
        "confidence": 0.85,
        "needs_human_review": True,
        "rationale": "Missing required field"
    }
    
    result = AIValidationResult(**data)
    
    assert result.status == "needs_review"
    assert len(result.issues) == 1
    assert result.issues[0].field == "patient.id"
