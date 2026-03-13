"""
Validation engine that orchestrates all validation rules.
Responsible for:
- Running all rules
- Aggregating issues
- Computing status, confidence, needs_human_review
- Returning ValidationResult
"""
from typing import List

from app.models.claim_models import ClaimInput
from app.models.validation_models import ValidationIssue, ValidationResult
from app.services.validation.rules import ALL_RULES


def run_validation(claim: ClaimInput) -> ValidationResult:
    """
    Run all validation rules on a claim and return aggregated result.
    
    Args:
        claim: The claim input to validate
        
    Returns:
        ValidationResult with status, issues, confidence, etc.
    """
    # Collect all issues from all rules
    all_issues: List[ValidationIssue] = []
    
    for rule in ALL_RULES:
        issues = rule(claim)
        all_issues.extend(issues)
    
    # Determine status: FAIL if any ERROR exists
    has_errors = any(issue.severity == "ERROR" for issue in all_issues)
    status = "FAIL" if has_errors else "PASS"
    
    # Confidence is always 1.0 for deterministic validation
    confidence = 1.0
    
    # Needs human review is always false for deterministic validation
    needs_human_review = False
    
    # Build rationale
    if len(all_issues) == 0:
        rationale = "All validation checks passed"
    else:
        error_count = sum(1 for issue in all_issues if issue.severity == "ERROR")
        warning_count = sum(1 for issue in all_issues if issue.severity == "WARNING")
        rationale = f"Found {error_count} error(s) and {warning_count} warning(s)"
    
    return ValidationResult(
        status=status,
        issues=all_issues,
        confidence=confidence,
        needs_human_review=needs_human_review,
        rationale=rationale
    )
