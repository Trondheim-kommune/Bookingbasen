"""Removed status from all slots

Revision ID: 4efdbda3b553
Revises: 449c8b35b869
Create Date: 2014-03-22 16:38:28.273550

"""

# revision identifiers, used by Alembic.
revision = '4efdbda3b553'
down_revision = '449c8b35b869'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

def upgrade():
    op.drop_column("slots", "status")
    op.drop_column("repeating_slots", "status")
    op.drop_column("strotime_slots", "status")
    ENUM(name="slot_status_types").drop(op.get_bind(), checkfirst=False)
    ENUM(name="strotime_slot_status_types").drop(op.get_bind(), checkfirst=False)


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
