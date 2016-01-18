"""Removed request_uri for slots and repeating slots

Revision ID: 449c8b35b869
Revises: 1b81c4cf5a5a
Create Date: 2014-03-22 15:50:29.543673

"""

# revision identifiers, used by Alembic.
revision = '449c8b35b869'
down_revision = '1b81c4cf5a5a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("slots", "request_uri")
    op.drop_column("repeating_slots", "request_uri")

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
