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
    op.add_column("attendees", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_attendees_owner_user_id_users",
        "attendees",
        "users",
        ["owner_user_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_attendees_owner_user_id_users", "attendees", type_="foreignkey")
    op.drop_column("attendees", "owner_user_id")
