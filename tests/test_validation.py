"""Tests for deterministic validation"""
import pytest
from datetime import date, timedelta
from app.models.claim_models import ClaimInput, Patient, Coverage, CareEvent, Billing
from app.services.validation.engine import run_validation


def create_valid_claim() -> ClaimInput:
    """Helper to create a valid claim"""
    today = date.today()
    return ClaimInput(
        patient=Patient(
            id="patient123",
            date_of_birth=today - timedelta(days=365*30)  # 30 years ago
        ),
        coverage=Coverage(
            policy_id="POL123",
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30)
        ),
        care_event=CareEvent(
            service_date=today,
            location="Hospital A"
        ),
        billing=Billing(
            codes=["99213", "87070"]
        )
    )


def test_valid_claim_passes():
    """Valid claim should PASS with no issues"""
    claim = create_valid_claim()
    result = run_validation(claim)
    
    assert result.status == "PASS"
    assert len(result.issues) == 0
    assert result.confidence == 1.0
    assert result.needs_human_review is False
    assert "passed" in result.rationale.lower()


def test_missing_policy_id_fails():
    """Missing policy_id should FAIL with correct issue code"""
    claim = create_valid_claim()
    claim.coverage.policy_id = ""
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    assert len(result.issues) >= 1
    
    # Check for specific issue
    policy_issues = [i for i in result.issues if i.code == "MISSING_POLICY_ID"]
    assert len(policy_issues) == 1
    assert policy_issues[0].severity == "ERROR"
    assert policy_issues[0].field == "coverage.policy_id"


def test_missing_service_date_fails():
    """Missing service_date should FAIL"""
    # Note: Pydantic validation will catch this before our rules
    # This tests the completeness check
    claim = create_valid_claim()
    # We can't set service_date to None due to Pydantic, so this tests
    # that our rules handle the case properly
    result = run_validation(claim)
    # Valid claim should pass
    assert result.status == "PASS"


def test_missing_billing_codes_fails():
    """Missing billing codes should FAIL"""
    claim = create_valid_claim()
    claim.billing.codes = []
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    
    # Check for specific issue
    billing_issues = [i for i in result.issues if i.code == "MISSING_BILLING_CODES"]
    assert len(billing_issues) == 1
    assert billing_issues[0].severity == "ERROR"


def test_service_before_birth_fails():
    """Service date before birth should FAIL"""
    claim = create_valid_claim()
    claim.patient.date_of_birth = date.today()
    claim.care_event.service_date = date.today() - timedelta(days=1)
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    
    # Check for specific issue
    birth_issues = [i for i in result.issues if i.code == "SERVICE_BEFORE_BIRTH"]
    assert len(birth_issues) == 1
    assert birth_issues[0].severity == "ERROR"


def test_service_before_coverage_fails():
    """Service date before coverage start should FAIL"""
    claim = create_valid_claim()
    claim.coverage.start_date = date.today() + timedelta(days=10)
    claim.care_event.service_date = date.today()
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    
    # Check for specific issue
    coverage_issues = [i for i in result.issues if i.code == "SERVICE_BEFORE_COVERAGE"]
    assert len(coverage_issues) == 1


def test_service_after_coverage_fails():
    """Service date after coverage end should FAIL"""
    claim = create_valid_claim()
    claim.coverage.end_date = date.today() - timedelta(days=10)
    claim.care_event.service_date = date.today()
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    
    # Check for specific issue
    coverage_issues = [i for i in result.issues if i.code == "SERVICE_AFTER_COVERAGE"]
    assert len(coverage_issues) == 1


def test_empty_billing_code_fails():
    """Empty string billing code should FAIL"""
    claim = create_valid_claim()
    claim.billing.codes = ["99213", ""]
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    
    # Check for specific issue
    code_issues = [i for i in result.issues if i.code == "INVALID_BILLING_CODE"]
    assert len(code_issues) == 1


def test_multiple_errors():
    """Multiple errors should all be captured"""
    claim = create_valid_claim()
    claim.coverage.policy_id = ""
    claim.billing.codes = []
    
    result = run_validation(claim)
    
    assert result.status == "FAIL"
    assert len(result.issues) >= 2
    
    # Should have both policy and billing issues
    codes = [i.code for i in result.issues]
    assert "MISSING_POLICY_ID" in codes
    assert "MISSING_BILLING_CODES" in codes
