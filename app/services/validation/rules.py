"""
Pure validation rules for claims.
Each rule is a pure function that takes ClaimInput and returns a list of ValidationIssue.
No database access. No side effects.
"""
from typing import List
from datetime import date

from app.models.claim_models import ClaimInput
from app.models.validation_models import ValidationIssue


def check_completeness(claim: ClaimInput) -> List[ValidationIssue]:
    """
    Check for missing required fields.
    
    Rules:
    - Missing policy_id → ERROR
    - Missing service_date → ERROR  
    - Missing billing codes → ERROR
    """
    issues = []
    
    # Check policy_id
    if not claim.coverage.policy_id or claim.coverage.policy_id.strip() == "":
        issues.append(ValidationIssue(
            code="MISSING_POLICY_ID",
            severity="ERROR",
            field="coverage.policy_id",
            message="Policy ID is required"
        ))
    
    # Check service_date
    if not claim.care_event.service_date:
        issues.append(ValidationIssue(
            code="MISSING_SERVICE_DATE",
            severity="ERROR",
            field="care_event.service_date",
            message="Service date is required"
        ))
    
    # Check billing codes
    if not claim.billing.codes or len(claim.billing.codes) == 0:
        issues.append(ValidationIssue(
            code="MISSING_BILLING_CODES",
            severity="ERROR",
            field="billing.codes",
            message="At least one billing code is required"
        ))
    
    return issues


def check_format(claim: ClaimInput) -> List[ValidationIssue]:
    """
    Check field formats.
    
    Rules:
    - Dates must be valid ISO dates (handled by Pydantic)
    - Codes must be non-empty strings
    """
    issues = []
    
    # Check billing codes are non-empty strings
    for idx, code in enumerate(claim.billing.codes):
        if not isinstance(code, str) or code.strip() == "":
            issues.append(ValidationIssue(
                code="INVALID_BILLING_CODE",
                severity="ERROR",
                field=f"billing.codes[{idx}]",
                message=f"Billing code at index {idx} must be a non-empty string"
            ))
    
    return issues


def check_logical_consistency(claim: ClaimInput) -> List[ValidationIssue]:
    """
    Check logical consistency between fields.
    
    Rules:
    - service_date >= patient.date_of_birth
    - coverage.start_date <= service_date <= coverage.end_date
    """
    issues = []
    
    # Check service_date >= date_of_birth
    if claim.care_event.service_date < claim.patient.date_of_birth:
        issues.append(ValidationIssue(
            code="SERVICE_BEFORE_BIRTH",
            severity="ERROR",
            field="care_event.service_date",
            message="Service date cannot be before patient's date of birth"
        ))
    
    # Check service_date within coverage period
    if claim.care_event.service_date < claim.coverage.start_date:
        issues.append(ValidationIssue(
            code="SERVICE_BEFORE_COVERAGE",
            severity="ERROR",
            field="care_event.service_date",
            message="Service date is before coverage start date"
        ))
    
    if claim.care_event.service_date > claim.coverage.end_date:
        issues.append(ValidationIssue(
            code="SERVICE_AFTER_COVERAGE",
            severity="ERROR",
            field="care_event.service_date",
            message="Service date is after coverage end date"
        ))
    
    return issues


# List of all validation rules
ALL_RULES = [
    check_completeness,
    check_format,
    check_logical_consistency,
]
