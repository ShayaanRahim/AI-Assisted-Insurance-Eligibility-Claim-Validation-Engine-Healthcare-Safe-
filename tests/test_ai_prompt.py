"""
Tests for AI prompt construction.

These tests verify that prompts contain all required elements for safe AI operation.
"""
import pytest
from app.services.validation.prompt import build_validation_prompt, get_prompt_version


def test_prompt_includes_claim_data():
    """Prompt should include the claim data"""
    claim_data = {
        "patient": {"id": "P123", "date_of_birth": "1990-01-01"},
        "coverage": {"policy_id": "POL456"}
    }
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "P123" in prompt
    assert "POL456" in prompt


def test_prompt_includes_deterministic_result():
    """Prompt should include the deterministic validation result"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {
        "status": "FAIL",
        "issues": [{"code": "MISSING_POLICY_ID"}]
    }
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "FAIL" in prompt
    assert "MISSING_POLICY_ID" in prompt


def test_prompt_includes_behavioral_constraints():
    """Prompt should include critical safety constraints"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    # Check for key constraint phrases
    assert "DO NOT guess" in prompt or "do not guess" in prompt.lower()
    assert "unknown" in prompt.lower()
    assert "confidence" in prompt.lower()


def test_prompt_defines_output_schema():
    """Prompt should explicitly define the output JSON schema"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    # Check for schema elements
    assert "status" in prompt
    assert "approved" in prompt
    assert "needs_review" in prompt
    assert "rejected" in prompt
    assert "unknown" in prompt
    assert "issues" in prompt
    assert "confidence" in prompt


def test_prompt_forbids_guessing():
    """Prompt should explicitly forbid guessing"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "guess" in prompt.lower()
    assert "assume" in prompt.lower() or "invent" in prompt.lower()


def test_prompt_allows_unknown_status():
    """Prompt should explicitly allow 'unknown' as a valid status"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "unknown" in prompt.lower()
    # Should be mentioned as a valid option
    assert '"unknown"' in prompt or "'unknown'" in prompt


def test_prompt_includes_json_only_instruction():
    """Prompt should instruct to return JSON only, no markdown"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "JSON" in prompt or "json" in prompt.lower()
    assert "markdown" in prompt.lower() or "no markdown" in prompt.lower()


def test_prompt_version_returns_string():
    """get_prompt_version should return a version string"""
    version = get_prompt_version()
    
    assert isinstance(version, str)
    assert len(version) > 0
    # Should look like a version (e.g., "v1")
    assert "v" in version.lower() or version[0].isdigit()


def test_prompt_mentions_advisory_role():
    """Prompt should clarify AI is advisory only"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "advisory" in prompt.lower() or "not make final" in prompt.lower()


def test_prompt_prefers_needs_review_over_guessing():
    """Prompt should instruct to prefer 'needs_review' when uncertain"""
    claim_data = {"patient": {"id": "P123"}}
    deterministic_result = {"status": "PASS"}
    
    prompt = build_validation_prompt(claim_data, deterministic_result)
    
    assert "needs_review" in prompt.lower()
    assert "prefer" in prompt.lower() or "uncertain" in prompt.lower()
