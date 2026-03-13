# Day 3 Implementation: Core API + Deterministic Validation Engine

## Overview

This document describes the Day 3 implementation of the healthcare claim validation system. The system provides deterministic validation rules for insurance claims with full auditability and traceability.

## Architecture

### Core Components

1. **Data Models** (`app/models/`)
   - `claim_models.py`: Pydantic models for claim input (ClaimInput) and responses
   - `validation_models.py`: Pydantic models for validation results (ValidationIssue, ValidationResult)

2. **Database Models** (`app/db/models.py`)
   - `Claim`: Stores raw claim JSON and status
   - `Validation`: Stores validation results with full history

3. **Validation Engine** (`app/services/validation/`)
   - `rules.py`: Pure functions implementing validation rules
   - `engine.py`: Orchestrates rules and produces ValidationResult

4. **API Endpoints** (`app/api/`)
   - `claims.py`: Claim creation and retrieval
   - `validation.py`: Deterministic validation endpoint

## API Endpoints

### POST /claims
Creates a new claim.

**Request Body:**
```json
{
  "patient": {
    "id": "patient123",
    "date_of_birth": "1990-01-01"
  },
  "coverage": {
    "policy_id": "POL123",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "care_event": {
    "service_date": "2024-06-15",
    "location": "Hospital A"
  },
  "billing": {
    "codes": ["99213", "87070"]
  }
}
```

**Response:**
```json
{
  "claim_id": "uuid-here"
}
```

### GET /claims/{claim_id}
Retrieves a claim with all its validation history.

**Response:**
```json
{
  "claim_id": "uuid",
  "status": "DRAFT",
  "created_at": "2024-06-15T10:00:00Z",
  "updated_at": "2024-06-15T10:00:00Z",
  "raw_claim": { ... },
  "validations": [
    {
      "validation_id": "uuid",
      "source": "deterministic",
      "result": { ... },
      "created_at": "2024-06-15T10:01:00Z"
    }
  ]
}
```

### POST /claims/{claim_id}/validate/deterministic
Runs deterministic validation on a claim.

**Response:**
```json
{
  "status": "PASS",
  "issues": [],
  "confidence": 1.0,
  "needs_human_review": false,
  "rationale": "All validation checks passed"
}
```

**Response (with errors):**
```json
{
  "status": "FAIL",
  "issues": [
    {
      "code": "MISSING_POLICY_ID",
      "severity": "ERROR",
      "field": "coverage.policy_id",
      "message": "Policy ID is required"
    }
  ],
  "confidence": 1.0,
  "needs_human_review": false,
  "rationale": "Found 1 error(s) and 0 warning(s)"
}
```

## Validation Rules

### Completeness Rules
- `MISSING_POLICY_ID`: Policy ID is required
- `MISSING_SERVICE_DATE`: Service date is required
- `MISSING_BILLING_CODES`: At least one billing code is required

### Format Rules
- `INVALID_BILLING_CODE`: Billing codes must be non-empty strings

### Logical Consistency Rules
- `SERVICE_BEFORE_BIRTH`: Service date cannot be before patient's date of birth
- `SERVICE_BEFORE_COVERAGE`: Service date must be after coverage start date
- `SERVICE_AFTER_COVERAGE`: Service date must be before coverage end date

## Claim Status Transitions

1. **DRAFT**: Initial state when claim is created
2. **READY_FOR_AI**: Validation passed, ready for AI review
3. **NEEDS_FIXES**: Validation failed, requires corrections

## Database Schema

### claims table
- `id`: UUID (primary key)
- `raw_claim_json`: JSON
- `status`: String (DRAFT, READY_FOR_AI, NEEDS_FIXES)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### validations table
- `id`: UUID (primary key)
- `claim_id`: UUID (foreign key to claims)
- `source`: String (deterministic)
- `result_json`: JSON (complete ValidationResult)
- `created_at`: Timestamp

## Key Design Decisions

1. **No AI or LLMs**: All validation is deterministic and rule-based
2. **Immutable Validation History**: Each validation run creates a new record, preserving full history
3. **Pure Functions**: Validation rules are pure functions with no side effects or database access
4. **Separation of Concerns**: Business logic is isolated from API routes
5. **Auditability**: All validation results are stored with timestamps and complete context

## Running the System

### Prerequisites
- PostgreSQL database running
- Python 3.12+
- Dependencies installed: `pip install -r requirements.txt`

### Database Setup
```bash
# Run migrations
alembic upgrade head
```

### Running the Server
```bash
uvicorn app.main:app --reload
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_validation.py
pytest tests/test_api.py
```

## Test Coverage

- ✅ All validation rules tested
- ✅ API endpoints tested
- ✅ Multiple validation runs create multiple records
- ✅ Claim status transitions verified
- ✅ Error handling tested

All 17 tests passing.

## Acceptance Criteria Status

✅ I can POST a claim and retrieve it
✅ Deterministic validation always returns schema-valid JSON
✅ Adding a new rule does NOT require touching API code
✅ Validation history is preserved
✅ Claim status transitions are predictable
✅ No AI or heuristics exist anywhere

## Adding New Validation Rules

To add a new validation rule:

1. Create a new function in `app/services/validation/rules.py`:
```python
def check_new_rule(claim: ClaimInput) -> List[ValidationIssue]:
    issues = []
    # Your validation logic here
    return issues
```

2. Add the function to the `ALL_RULES` list at the bottom of `rules.py`

3. No changes needed to API code or database

The engine will automatically run your new rule!
