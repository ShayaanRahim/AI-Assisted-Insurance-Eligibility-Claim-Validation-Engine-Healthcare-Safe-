"""
LLM prompt construction for AI claim validation.

This module is responsible for building prompts that:
- Enforce structured output
- Prevent hallucination
- Allow uncertainty ("unknown" status)
- Maintain safety over accuracy
"""
import json
from typing import Dict, Any


# Version for tracking prompt changes over time
PROMPT_VERSION = "v1"


def build_validation_prompt(claim_data: Dict[str, Any], deterministic_result: Dict[str, Any]) -> str:
    """
    Constructs the prompt for AI validation.
    
    The prompt has four sections:
    1. System Role - What the AI is
    2. Input Data - The claim and prior validation
    3. Behavioral Constraints - Safety rules
    4. Decision Instructions - How to respond
    
    Args:
        claim_data: The raw claim input
        deterministic_result: Results from deterministic validation
        
    Returns:
        Complete prompt string
    """
    
    # Section 1: System Role
    system_role = """You are an AI assistant for healthcare insurance claim validation.
You are ADVISORY ONLY. Your role is to detect potential issues, not to make final approval decisions.
You work AFTER deterministic rules have already run."""
    
    # Section 2: Input Data
    input_section = f"""
INPUT DATA:

Claim Data:
{json.dumps(claim_data, indent=2)}

Deterministic Validation Result:
{json.dumps(deterministic_result, indent=2)}
"""
    
    # Section 3: Behavioral Constraints
    constraints = """
CRITICAL CONSTRAINTS (YOU MUST FOLLOW THESE):

1. DO NOT guess or assume missing data
2. DO NOT invent coverage rules
3. DO NOT add fields that don't exist in the input
4. If you are uncertain, return "unknown" status
5. If confidence is low, reduce your confidence score
6. Prefer "needs_review" over guessing
7. You must output ONLY valid JSON, no markdown, no comments
8. If deterministic validation found errors, you should flag for review

VALID STATUS VALUES:
- "approved": High confidence, no significant issues
- "needs_review": Uncertain or potential issues detected
- "rejected": Clear problems that prevent approval
- "unknown": Insufficient information to make assessment

VALID ISSUE TYPES:
- "missing_field": Required data is missing
- "inconsistency": Data conflicts between fields
- "coverage_risk": Potential coverage or eligibility issue

VALID SEVERITY LEVELS:
- "low": Minor issue, unlikely to block claim
- "medium": Moderate concern, may need clarification
- "high": Serious issue, likely blocks claim
"""
    
    # Section 4: Decision Instructions
    decision_instructions = """
OUTPUT SCHEMA (STRICTLY ENFORCE):

You must return ONLY a JSON object with this exact structure:

{
  "status": "approved" | "needs_review" | "rejected" | "unknown",
  "issues": [
    {
      "type": "missing_field" | "inconsistency" | "coverage_risk",
      "field": "string (dot notation like 'coverage.policy_id')",
      "severity": "low" | "medium" | "high",
      "explanation": "string (human-readable explanation)"
    }
  ],
  "confidence": 0.0 to 1.0 (float),
  "needs_human_review": true | false,
  "rationale": "string (explain your decision)"
}

DECISION GUIDELINES:

1. If deterministic validation status is "FAIL", strongly consider "needs_review" or "rejected"
2. If you detect any inconsistency between dates, coverage, or billing, create an issue
3. If coverage dates seem suspicious, flag as "coverage_risk"
4. Set confidence based on:
   - High (0.8-1.0): Clear case, all data present and consistent
   - Medium (0.5-0.79): Some ambiguity or minor issues
   - Low (0.0-0.49): Significant uncertainty or missing data
5. Always set needs_human_review = true if:
   - Confidence < 0.75
   - Status is "unknown"
   - Status is "rejected"
   - You find any "high" severity issues

EXAMPLE OUTPUT (DO NOT INCLUDE MARKDOWN):

{
  "status": "needs_review",
  "issues": [
    {
      "type": "coverage_risk",
      "field": "care_event.service_date",
      "severity": "medium",
      "explanation": "Service date is very close to coverage end date, may need verification"
    }
  ],
  "confidence": 0.65,
  "needs_human_review": true,
  "rationale": "Claim appears valid but proximity to coverage end date warrants human review for potential timing issues."
}

Now analyze the claim and return your assessment as JSON ONLY:
"""
    
    # Combine all sections
    full_prompt = f"{system_role}\n\n{input_section}\n{constraints}\n{decision_instructions}"
    
    return full_prompt


def get_prompt_version() -> str:
    """Returns the current prompt version for audit tracking"""
    return PROMPT_VERSION
