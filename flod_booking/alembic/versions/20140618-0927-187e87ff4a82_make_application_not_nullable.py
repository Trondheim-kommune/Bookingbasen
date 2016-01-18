"""Make application not nullable

Revision ID: 187e87ff4a82
Revises: 436f5bd9fd4
Create Date: 2014-06-18 09:27:55.331124

"""

# revision identifiers, used by Alembic.
revision = '187e87ff4a82'
down_revision = '436f5bd9fd4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    tables = ('slots',
              'strotime_slots',
              'slot_requests',
              'repeating_slots',
              'repeating_slot_requests')
    for table in tables:
        op.alter_column(table,
                        'application_id',
                        nullable=False)

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
