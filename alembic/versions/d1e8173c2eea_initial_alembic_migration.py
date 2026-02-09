"""Initial alembic migration

Revision ID: d1e8173c2eea
Revises: 
Create Date: 2026-02-09 21:55:13.383599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e8173c2eea'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("histories") as batch_op:
        batch_op.drop_constraint("histories_portfolio_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "histories_portfolio_id_fkey",
            "portfolios",
            ["portfolio_id"],
            ["id"],
            ondelete="CASCADE"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("histories") as batch_op:
        batch_op.drop_constraint("histories_portfolio_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "histories_portfolio_id_fkey",
            "portfolios",
            ["portfolio_id"],
            ["id"]
        )
