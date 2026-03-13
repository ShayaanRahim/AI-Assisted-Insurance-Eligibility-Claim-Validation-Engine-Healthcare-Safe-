from fastapi import FastAPI
from app.api import claims, validation, ai_validation

app = FastAPI(title="AI Claim Validation")

# Include routers
app.include_router(claims.router)
app.include_router(validation.router)
app.include_router(ai_validation.router)

@app.get("/health")
def health():
    return {"status": "ok"}
