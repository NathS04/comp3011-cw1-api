"""add event ownership

Revision ID: 8c8851f64d1d
Revises: 290a4b3ac4a5
Create Date: 2026-03-17 19:23:58.704212

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8c8851f64d1d'
down_revision: Union[str, Sequence[str], None] = '290a4b3ac4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('events') as batch_op:
        batch_op.add_column(sa.Column('created_by_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_events_created_by_user_id_users', 'users', ['created_by_user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('events') as batch_op:
        batch_op.drop_constraint('fk_events_created_by_user_id_users', type_='foreignkey')
        batch_op.drop_column('created_by_user_id')
    # ### end Alembic commands ###
