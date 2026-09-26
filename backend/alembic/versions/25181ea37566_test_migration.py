"""test migration

Revision ID: 25181ea37566
Revises: e92586c5f507
Create Date: 2026-09-27 02:51:05.774572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25181ea37566'
down_revision: Union[str, Sequence[str], None] = 'e92586c5f507'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
