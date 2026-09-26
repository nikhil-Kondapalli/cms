"""Add role to user

Revision ID: 403fce6a0406
Revises: 85d8da37e8a4
Create Date: 2026-09-19 10:11:47.721080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '403fce6a0406'
down_revision: Union[str, Sequence[str], None] = '85d8da37e8a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    userrole = sa.Enum('admin', 'user', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', userrole, server_default='user', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    userrole = sa.Enum('admin', 'user', name='userrole')
    userrole.drop(op.get_bind(), checkfirst=True)
