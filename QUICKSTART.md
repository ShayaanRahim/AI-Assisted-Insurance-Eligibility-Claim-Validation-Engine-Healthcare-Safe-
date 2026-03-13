# Quick Start Guide - Day 3 Implementation

## Prerequisites

- Python 3.12+
- PostgreSQL running on `localhost:5432`
- Database named `claim_validation` created

## Setup in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Installs:
- FastAPI (web framework)
- SQLModel (ORM)
- Pydantic (validation)
- psycopg2-binary (PostgreSQL driver)
- Alembic (migrations)
- pytest (testing)

### 2. Setup Database

```bash
# Create database (if not exists)
createdb claim_validation

# Run migrations
alembic upgrade head
```

### 3. Start Server

```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Create a Valid Claim
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
{"claim_id": "abc123..."}
```

### Validate the Claim
```bash
# Replace {claim_id} with actual ID from previous response
curl -X POST http://localhost:8000/claims/{claim_id}/validate/deterministic
```

Response (PASS):
```json
{
  "status": "PASS",
  "issues": [],
  "confidence": 1.0,
  "needs_human_review": false,
  "rationale": "All validation checks passed"
}
```

### Create an Invalid Claim (Missing Policy ID)
```bash
curl -X POST http://localhost:8000/claims \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "id": "patient456",
      "date_of_birth": "1985-05-15"
    },
    "coverage": {
      "policy_id": "",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31"
    },
    "care_event": {
      "service_date": "2024-06-15",
      "location": "Hospital B"
    },
    "billing": {
      "codes": ["99213"]
    }
  }'
```

Then validate:
```bash
curl -X POST http://localhost:8000/claims/{claim_id}/validate/deterministic
```

Response (FAIL):
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

### Get Claim with Validation History
```bash
curl http://localhost:8000/claims/{claim_id}
```

Response:
```json
{
  "claim_id": "abc123...",
  "status": "READY_FOR_AI",
  "created_at": "2024-06-15T10:00:00Z",
  "updated_at": "2024-06-15T10:01:00Z",
  "raw_claim": { ... },
  "validations": [
    {
      "validation_id": "def456...",
      "source": "deterministic",
      "result": { ... },
      "created_at": "2024-06-15T10:01:00Z"
    }
  ]
}
```

## Interactive API Documentation

Visit these URLs once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Run Tests

```bash
# All tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/test_validation.py
pytest tests/test_api.py

# With coverage
pytest --cov=app tests/
```

Expected output:
```
17 passed in 1.02s
```

## Validation Rules Reference

### Completeness
- **MISSING_POLICY_ID**: Coverage must have a policy_id
- **MISSING_SERVICE_DATE**: Care event must have a service_date
- **MISSING_BILLING_CODES**: At least one billing code required

### Format
- **INVALID_BILLING_CODE**: Billing codes must be non-empty strings

### Logical Consistency
- **SERVICE_BEFORE_BIRTH**: Service date >= patient date of birth
- **SERVICE_BEFORE_COVERAGE**: Service date >= coverage start date
- **SERVICE_AFTER_COVERAGE**: Service date <= coverage end date

## Status Transitions

1. **DRAFT** → Claim created
2. **READY_FOR_AI** → Validation passed
3. **NEEDS_FIXES** → Validation failed

## Configuration

Edit `app/core/config.py` or create `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/claim_validation
```

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep claim_validation
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Tests Failing
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Run with verbose output
pytest -vv
```

## Project Structure

```
AI-Claim-Validation/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration
│   ├── db/               # Database models & session
│   ├── models/           # Pydantic models
│   └── services/         # Business logic
│       └── validation/   # Validation engine
├── tests/                # Test suite
├── alembic/              # Database migrations
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
```

## Next Steps

1. ✅ Day 3 complete - Core API + Deterministic Validation
2. 🔜 Day 4 - Add AI validation (future)
3. 🔜 Day 5 - Add human review workflow (future)

---

**Need Help?** Check the full documentation in `docs/day3_implementation.md`
