# AI-Assisted Claim Validation System

A production-grade backend for healthcare insurance claim validation with deterministic rules and AI-powered advisory analysis.

## 🎯 Project Status

- ✅ **Day 3 Complete**: Deterministic validation engine
- ✅ **Day 4 Complete**: AI validation layer
- 🔜 **Day 5**: Human review workflow (future)

**Tests**: 47/47 passing  
**Code Quality**: No linter errors  
**Production Ready**: Yes

---

## Core Features

### Deterministic Validation (Day 3)
- **Rule-based validation** with 7 explicit rules
- **100% confidence** - no uncertainty
- **Instant results** - no API calls
- **Complete audit trail** - every decision traceable
- **Status transitions**: DRAFT → READY_FOR_AI / NEEDS_FIXES

### AI Validation (Day 4)
- **Advisory analysis** powered by GPT-4o-mini
- **Confidence scoring** (0.0-1.0)
- **Can say "unknown"** when uncertain
- **Safe fallback** if AI fails
- **6 guardrails** override unsafe decisions
- **Complete metadata** tracking

### System Design
- **Structured data handling** - Pydantic schemas
- **Human-in-the-loop** - AI is advisory only
- **Auditability** - Full validation history preserved
- **Safety first** - Multiple layers of protection
- **Extensible** - Add new rules without changing API

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- OpenAI API key (for AI validation)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
createdb claim_validation
alembic upgrade head

# Set OpenAI API key (for AI validation)
export OPENAI_API_KEY="your-key"

# Start server
uvicorn app.main:app --reload
```

### Run Tests

```bash
pytest tests/ -v
# Expected: 47 passed in ~1.4s
```

---

## API Endpoints

### Claims
- `POST /claims` - Create a new claim
- `GET /claims/{claim_id}` - Retrieve claim with full history

### Validation
- `POST /claims/{claim_id}/validate/deterministic` - Run rule-based validation
- `POST /claims/{claim_id}/validate/ai` - Run AI-powered analysis (requires deterministic first)

### Example Flow

```bash
# 1. Create claim
curl -X POST http://localhost:8000/claims -H "Content-Type: application/json" -d '{...}'

# 2. Run deterministic validation
curl -X POST http://localhost:8000/claims/{id}/validate/deterministic

# 3. Run AI validation (optional, advisory only)
curl -X POST http://localhost:8000/claims/{id}/validate/ai

# 4. View complete history
curl http://localhost:8000/claims/{id}
```

---

## Documentation

- **[Day 3 Implementation](DAY3_SUMMARY.md)** - Deterministic validation
- **[Day 4 Implementation](DAY4_IMPLEMENTATION.md)** - AI validation layer
- **[Quick Start Guide](QUICKSTART.md)** - Day 3 getting started
- **[AI Quick Start](DAY4_QUICKSTART.md)** - Day 4 getting started
- **[Status Reports](DAY4_STATUS_REPORT.md)** - Complete status

---

## Architecture

```
POST /claims
    ↓
Validate with Pydantic
    ↓
Store in PostgreSQL
    ↓
[User triggers validation]
    ↓
1. Deterministic Validation
    ├─→ 7 rules (completeness, format, logic)
    ├─→ Confidence: 1.0
    └─→ Status: PASS/FAIL
    ↓
2. AI Validation (optional)
    ├─→ Call OpenAI with structured output
    ├─→ Apply 6 guardrails
    ├─→ Confidence: 0.0-1.0
    └─→ Status: approved/needs_review/rejected/unknown
    ↓
Store validation history
    ↓
Return to client
```

---

## Key Design Principles

1. **Safety Over Speed** - AI can say "unknown" rather than guess
2. **Deterministic First** - Hard rules before AI analysis  
3. **Advisory AI** - Never auto-approves without human review
4. **Fail Gracefully** - Safe fallback if AI unavailable
5. **Complete Audit** - Every decision is traceable
6. **Schema Enforced** - No free-text, JSON only

---

## Test Coverage

- **Deterministic tests** (17): All validation rules
- **AI guardrails tests** (10): Safety rules
- **AI models tests** (10): Schema validation
- **AI prompt tests** (10): Prompt structure
- **Total**: 47 tests, 100% passing

---

## Guardrails (AI Safety)

6 deterministic rules that override AI:

1. Low confidence (< 0.75) → force human review
2. Status "unknown" → force human review
3. Status "rejected" → force human review
4. Status "approved" + low confidence → change to "needs_review"
5. High severity issues → force human review
6. Deterministic FAIL + AI "approved" → override to "needs_review"

**These cannot be bypassed by AI.**

---

## What's Included

✅ RESTful API (FastAPI)  
✅ PostgreSQL database  
✅ Alembic migrations  
✅ Pydantic schemas  
✅ Deterministic validation rules  
✅ AI validation with OpenAI  
✅ Post-processing guardrails  
✅ Complete test suite  
✅ Comprehensive documentation  

## What's NOT Included

❌ Real billing system  
❌ Payer API integration  
❌ HIPAA certification  
❌ User interface  
❌ Authentication  
❌ Model fine-tuning  

This is a **backend-only** system for validation logic.

---

## Technology Stack

- **Framework**: FastAPI 0.128.0
- **Database**: PostgreSQL + SQLModel
- **Validation**: Pydantic 2.11.9
- **AI**: OpenAI API (gpt-4o-mini)
- **Migrations**: Alembic
- **Testing**: Pytest

---

## Configuration

### Required
```bash
export OPENAI_API_KEY="your-api-key"  # For AI validation
```

### Optional
- Database URL: Set in `app/core/config.py`
- AI model: Default `gpt-4o-mini`
- Confidence threshold: Default `0.75`

---

## Project Structure

```
app/
├── main.py                     # FastAPI app
├── api/                        # API endpoints
│   ├── claims.py               # Claims CRUD
│   ├── validation.py           # Deterministic validation
│   └── ai_validation.py        # AI validation
├── models/                     # Pydantic schemas
│   ├── claim_models.py
│   ├── validation_models.py
│   └── ai_validation_models.py
├── services/                   # Business logic
│   ├── ai_validator.py         # AI service
│   └── validation/
│       ├── rules.py            # Deterministic rules
│       ├── engine.py           # Rule orchestration
│       ├── prompt.py           # LLM prompt template
│       └── guardrails.py       # Post-processing safety
└── db/                         # Database
    ├── models.py               # SQLModel tables
    └── session.py              # DB session

tests/                          # Test suite (47 tests)
alembic/                        # Database migrations
docs/                           # Documentation
```

---

## Contributing

This is a demonstration project for building production-grade healthcare systems. 

**Constraints followed**:
- No LLMs in deterministic validation
- No business logic in API routes
- No database access in validation rules
- No overwriting historical records
- AI is advisory only

---

## License

See [LICENSE](LICENSE) file.

---

## Support

For questions or issues, check the documentation:
- [Day 3 Implementation](DAY3_SUMMARY.md)
- [Day 4 Implementation](DAY4_IMPLEMENTATION.md)
- [Quick Start Guide](QUICKSTART.md)

---

**Built with a focus on safety, auditability, and production readiness.**