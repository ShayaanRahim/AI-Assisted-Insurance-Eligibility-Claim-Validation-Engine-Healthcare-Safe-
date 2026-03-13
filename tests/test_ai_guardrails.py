"""
Tests for AI validation guardrails.

These tests verify that post-processing rules correctly enforce safety constraints.
"""
import pytest
from app.models.ai_validation_models import AIValidationResult, AIValidationIssue
from app.services.validation.guardrails import (
    apply_guardrails, 
    validate_against_deterministic,
    get_confidence_threshold
)


def test_low_confidence_forces_human_review():
    """Low confidence (< 0.75) should force needs_human_review = true"""
    result = AIValidationResult(
        status="needs_review",
        issues=[],
        confidence=0.65,
        needs_human_review=False,  # AI said no
        rationale="Some reason"
    )
    
    result = apply_guardrails(result)
    
    # Guardrail should have forced human review
    assert result.needs_human_review is True


def test_unknown_status_forces_human_review():
    """Status 'unknown' should force needs_human_review = true"""
    result = AIValidationResult(
        status="unknown",
        issues=[],
        confidence=0.9,  # Even with high confidence
        needs_human_review=False,
        rationale="Cannot determine"
    )
    
    result = apply_guardrails(result)
    
    assert result.needs_human_review is True


def test_rejected_status_forces_human_review():
    """Status 'rejected' should force needs_human_review = true"""
    result = AIValidationResult(
        status="rejected",
        issues=[],
        confidence=0.95,
        needs_human_review=False,
        rationale="Clear rejection"
    )
    
    result = apply_guardrails(result)
    
    assert result.needs_human_review is True


def test_approved_with_low_confidence_changed_to_needs_review():
    """Cannot approve with confidence < 0.75"""
    result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.65,
        needs_human_review=False,
        rationale="Looks good"
    )
    
    result = apply_guardrails(result)
    
    # Status should be changed
    assert result.status == "needs_review"
    assert result.needs_human_review is True
    assert "GUARDRAIL APPLIED" in result.rationale


def test_high_severity_issue_forces_human_review():
    """High severity issues should force human review"""
    result = AIValidationResult(
        status="needs_review",
        issues=[
            AIValidationIssue(
                type="coverage_risk",
                field="coverage.policy_id",
                severity="high",
                explanation="Critical issue"
            )
        ],
        confidence=0.9,
        needs_human_review=False,
        rationale="Has issue"
    )
    
    result = apply_guardrails(result)
    
    assert result.needs_human_review is True


def test_approved_with_high_confidence_passes():
    """Valid approval with high confidence should pass through"""
    result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.95,
        needs_human_review=False,
        rationale="All checks pass"
    )
    
    original_status = result.status
    result = apply_guardrails(result)
    
    # Should not be modified
    assert result.status == original_status
    assert result.needs_human_review is False


def test_deterministic_fail_prevents_ai_approval():
    """AI cannot approve if deterministic validation failed"""
    ai_result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.95,
        needs_human_review=False,
        rationale="Looks good"
    )
    
    deterministic_result = {
        "status": "FAIL",
        "issues": [{"code": "MISSING_POLICY_ID"}]
    }
    
    ai_result = validate_against_deterministic(ai_result, deterministic_result)
    
    # Status should be overridden
    assert ai_result.status == "needs_review"
    assert ai_result.needs_human_review is True
    assert "GUARDRAIL APPLIED" in ai_result.rationale
    assert "Deterministic validation found errors" in ai_result.rationale


def test_deterministic_pass_allows_ai_approval():
    """AI can approve if deterministic validation passed"""
    ai_result = AIValidationResult(
        status="approved",
        issues=[],
        confidence=0.95,
        needs_human_review=False,
        rationale="Looks good"
    )
    
    deterministic_result = {
        "status": "PASS",
        "issues": []
    }
    
    original_status = ai_result.status
    ai_result = validate_against_deterministic(ai_result, deterministic_result)
    
    # Should not be modified
    assert ai_result.status == original_status


def test_confidence_threshold_value():
    """Verify the confidence threshold is set correctly"""
    threshold = get_confidence_threshold()
    assert threshold == 0.75


def test_multiple_guardrails_applied():
    """Multiple guardrails should work together"""
    result = AIValidationResult(
        status="approved",
        issues=[
            AIValidationIssue(
                type="inconsistency",
                field="billing.codes",
                severity="high",
                explanation="Issue"
            )
        ],
        confidence=0.65,  # Low confidence
        needs_human_review=False,
        rationale="Approved"
    )
    
    result = apply_guardrails(result)
    
    # Should be changed to needs_review due to low confidence
    assert result.status == "needs_review"
    # Should be marked for human review due to both low confidence AND high severity
    assert result.needs_human_review is True
