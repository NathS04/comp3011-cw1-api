"""add attendee ownership

Revision ID: b1f6d6cb5d7d
Revises: 8c8851f64d1d
Create Date: 2026-03-17 19:55:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1f6d6cb5d7d"
down_revision: Union[str, Sequence[str], None] = "8c8851f64d1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('attendees') as batch_op:
        batch_op.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_attendees_owner_user_id_users",
            "users",
            ["owner_user_id"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('attendees') as batch_op:
        batch_op.drop_constraint("fk_attendees_owner_user_id_users", type_="foreignkey")
        batch_op.drop_column("owner_user_id")
