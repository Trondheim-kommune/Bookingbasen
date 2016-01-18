"""Remove resource column from slots

Revision ID: 412efb4b1c45
Revises: 187e87ff4a82
Create Date: 2014-06-18 09:32:58.121394

"""

# revision identifiers, used by Alembic.
revision = '412efb4b1c45'
down_revision = '187e87ff4a82'

from alembic import op
import sqlalchemy as sa


def upgrade():
    tables = ('slot_requests',
              'repeating_slot_requests')
    for table in tables:
        op.drop_column(table, 'resource_id')


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
