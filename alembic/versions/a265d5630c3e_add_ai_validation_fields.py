"""add_ai_validation_fields

Revision ID: a265d5630c3e
Revises: c1e4c0bcef7b
Create Date: 2026-02-03 18:24:17.203784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a265d5630c3e'
down_revision: Union[str, Sequence[str], None] = 'c1e4c0bcef7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI validation fields to validations table."""
    # Add AI-specific columns to validations table
    op.add_column('validations', sa.Column('model_name', sa.String(), nullable=True))
    op.add_column('validations', sa.Column('prompt_version', sa.String(), nullable=True))
    op.add_column('validations', sa.Column('input_hash', sa.String(), nullable=True))
    op.add_column('validations', sa.Column('confidence_score', sa.Float(), nullable=True))
    op.add_column('validations', sa.Column('needs_human_review', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add index on input_hash for deduplication queries
    op.create_index(op.f('ix_validations_input_hash'), 'validations', ['input_hash'], unique=False)


def downgrade() -> None:
    """Remove AI validation fields from validations table."""
    op.drop_index(op.f('ix_validations_input_hash'), table_name='validations')
    op.drop_column('validations', 'needs_human_review')
    op.drop_column('validations', 'confidence_score')
    op.drop_column('validations', 'input_hash')
    op.drop_column('validations', 'prompt_version')
    op.drop_column('validations', 'model_name')
