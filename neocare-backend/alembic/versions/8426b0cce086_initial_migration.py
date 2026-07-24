"""initial migration

Revision ID: 8426b0cce086
Revises: 71301dd9b9ca
Create Date: 2026-07-05 19:06:49.995859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8426b0cce086'
down_revision: Union[str, Sequence[str], None] = '71301dd9b9ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """La migración estaba vacía (pass) y se completa a mano"""
    #cada tabla se crea DESPUES de aquella a la que apunta (FK)

    op.create_table(
        'users', 
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    op.create_table(
        'boards',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    op.create_table(
        'board_lists',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('board_id', sa.Integer(), sa.ForeignKey('boards_id', ondelete='CASCADE=')),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'cards',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),    
        sa.Column('list_id', sa.Integer(), sa.ForeignKey("board_lists.id", ondelete="CASCADE")),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order',sa.Integer(), nullable=False, default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at',sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('completed_at',sa.DateTime(timezone=True), nullable=True) ,
    )

    op.create_table(
        'work_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('card_id', sa.Integer(), sa.ForeignKey("cards.id", ondelete="CASCADE")),
        sa.Column('user_id',sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column('hours',sa.Float(), nullable=False),  
        sa.Column('date',sa.DateTime(timezone=True), nullable=False),
        sa.Column('note',sa.String(200), nullable=True), 
        sa.Column('is_automatic', sa.Boolean(), nullable=False, default=False),
    )

    op.create_table(
        'labels',    
        sa.Column('id',sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), nullable=False),  
        sa.Column('board_id',sa.Integer(), sa.ForeignKey("boards.id", ondelete="CASCADE"))
    )


def downgrade() -> None:
    """Se borran en el orden inverso al de creación para no romper las claves foráneas"""
    op.drop_table('labels')
    op.drop_table('work_logs')
    op.drop_table('cards')
    op.drop_table('board_lists')
    op.drop_table('boards')
    op.drop_table('users')