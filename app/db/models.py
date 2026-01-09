from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

class Claim(str, Enum):
    draft = "draft"
    validated = "validated"
    rejected = "rejected"
    needs_review = "needs_review"

class Validation(str, Enum):
    rules_engine = "rules_engine"
    ai = "ai"

class Review(str, Enum):
    approved = "approved"
    overriden = "overriden"
    rejected = "rejected"


class Claim(SQLModel, table=True):
    __tablename__ = "claims"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    patient_payload: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    coverage_payload: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    claim_payload: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))

    status: Claim = Field(default=Claim.draft, nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )


class Validation(SQLModel, table=True):
    __tablename__ = "validations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    claim_id: UUID = Field(foreign_key="claims.id", index=True, nullable=False)

    source: Validation = Field(nullable=False)

    model_name: Optional[str] = Field(default=None)
    prompt_version: Optional[str] = Field(default=None)

    input_hash: str = Field(nullable=False, index=True)

    result_payload: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))

    confidence_score: Optional[float] = Field(default=None)
    needs_human_review: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )


class ReviewEvent(SQLModel, table=True):
    __tablename__ = "review_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    claim_id: UUID = Field(foreign_key="claims.id", index=True, nullable=False)
    validation_id: UUID = Field(foreign_key="validations.id", index=True, nullable=False)

    reviewer_role: str = Field(default="reviewer", nullable=False)
    decision: Review = Field(nullable=False)

    reviewer_notes: Optional[str] = Field(default=None)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )



