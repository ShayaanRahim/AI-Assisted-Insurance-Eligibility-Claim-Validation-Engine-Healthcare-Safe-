# Day 4 Quick Start: AI Validation

## Prerequisites

- Day 3 implementation complete
- OpenAI API key

## Setup (3 steps)

### 1. Install Dependencies

```bash
pip install openai
```

### 2. Run Database Migration

```bash
alembic upgrade head
```

This adds AI validation fields to the `validations` table.

### 3. Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage Example

### Step 1: Create a Claim

```bash
curl -X POST http://localhost:8000/claims \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Response:
```json
{"claim_id": "abc-123..."}
```

### Step 2: Run Deterministic Validation (Required First)

```bash
curl -X POST http://localhost:8000/claims/{claim_id}/validate/deterministic
```

Response:
```json
{
  "status": "PASS",
  "issues": [],
  "confidence": 1.0,
  "needs_human_review": false,
  "rationale": "All validation checks passed"
}
```

### Step 3: Run AI Validation

```bash
curl -X POST http://localhost:8000/claims/{claim_id}/validate/ai
```

Response:
```json
{
  "status": "approved",
  "issues": [],
  "confidence": 0.95,
  "needs_human_review": false,
  "rationale": "All data present and consistent. Coverage is active. No red flags detected."
}
```

## Example with Issues

If AI detects potential problems:

```json
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
  "confidence": 0.72,
  "needs_human_review": true,
  "rationale": "Claim appears valid but proximity to coverage end date warrants human review"
}
```

## AI Can Say "Unknown"

If AI lacks sufficient information:

```json
{
  "status": "unknown",
  "issues": [
    {
      "type": "missing_field",
      "field": "coverage.policy_id",
      "severity": "high",
      "explanation": "Cannot verify coverage without policy ID"
    }
  ],
  "confidence": 0.4,
  "needs_human_review": true,
  "rationale": "Insufficient information to make a determination. Manual review required."
}
```

## Safe Fallback (When AI Fails)

If the AI service fails, you get:

```json
{
  "status": "needs_review",
  "issues": [],
  "confidence": 0.0,
  "needs_human_review": true,
  "rationale": "AI validation unavailable; requires manual review."
}
```

The system never crashes on AI failure.

## Guardrails in Action

### Example: Low Confidence Blocked

AI tries to approve with low confidence (0.65):
- **Guardrail overrides** to "needs_review"
- Forces `needs_human_review = true`
- Adds "[GUARDRAIL APPLIED]" to rationale

### Example: Deterministic Failure

AI tries to approve, but deterministic validation found errors:
- **Guardrail overrides** to "needs_review"
- Adds explanation about deterministic failure

## View Full Claim History

```bash
curl http://localhost:8000/claims/{claim_id}
```

Response includes:
- Claim metadata
- Raw claim data
- All validations (deterministic + AI) ordered by time

```json
{
  "claim_id": "abc-123",
  "status": "DRAFT",
  "raw_claim": {...},
  "validations": [
    {
      "validation_id": "val-1",
      "source": "deterministic",
      "result": {...},
      "created_at": "2024-06-15T10:00:00Z"
    },
    {
      "validation_id": "val-2",
      "source": "llm",
      "result": {...},
      "created_at": "2024-06-15T10:01:00Z"
    }
  ]
}
```

## Run Tests

```bash
# All tests (47 total)
pytest tests/ -v

# Just AI tests (30 tests)
pytest tests/test_ai_* -v
```

Expected output: **47 passed**

## Configuration

### Change Model

Edit `app/api/ai_validation.py`:

```python
ai_service = AIValidationService(
    api_key=api_key,
    model_name="gpt-4"  # Change here
)
```

### Adjust Confidence Threshold

Edit `app/services/validation/guardrails.py`:

```python
CONFIDENCE_THRESHOLD = 0.80  # Default is 0.75
```

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"

```bash
export OPENAI_API_KEY="your-key"
```

### "Deterministic validation must be run first"

Run deterministic validation before AI validation:
```bash
curl -X POST http://localhost:8000/claims/{claim_id}/validate/deterministic
```

### AI Timeout

Default timeout is 30 seconds. If you see timeouts, check:
1. OpenAI API status
2. Network connectivity
3. API key validity

The system will return safe fallback after 2 retries.

## What's Different from Day 3?

| Feature | Day 3 | Day 4 |
|---------|-------|-------|
| Validation type | Deterministic rules | AI analysis |
| Confidence | Always 1.0 | 0.0-1.0 |
| Can be uncertain | No | Yes ("unknown" status) |
| Can fail | No | Yes (safe fallback) |
| Output | Rule violations | Contextual analysis |

## Key Safety Features

1. **Schema Enforcement**: AI must return valid JSON
2. **Guardrails**: 6 deterministic rules override AI
3. **Safe Fallback**: Never crashes on AI failure
4. **Audit Trail**: Full metadata tracked
5. **Advisory Only**: AI cannot make final decisions

## Next Steps

1. ✅ Day 3 complete - Deterministic validation
2. ✅ Day 4 complete - AI validation layer
3. 🔜 Day 5 - Human review workflow (future)

---

**Need Help?** Check `DAY4_IMPLEMENTATION.md` for detailed documentation.
