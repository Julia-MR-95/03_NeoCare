"""añade seguimiento automático de horas (completed_at + is_automatic)

Revision ID: 6aaad26c0d54
Revises: 8426b0cce086
Create Date: 2026-07-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6aaad26c0d54'
down_revision: Union[str, Sequence[str], None] = '8426b0cce086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cards', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'work_logs',
        sa.Column('is_automatic', sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('work_logs', 'is_automatic')
    op.drop_column('cards', 'completed_at')