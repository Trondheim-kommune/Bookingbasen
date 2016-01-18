"""Improved application to slot foreign keys

Revision ID: 1b81c4cf5a5a
Revises: 2e66e9dee225
Create Date: 2014-03-22 13:21:41.787602

"""

# revision identifiers, used by Alembic.
revision = '1b81c4cf5a5a'
down_revision = '2e66e9dee225'

from alembic import op
import sqlalchemy as sa


def upgrade():
    slot_types = ["strotime_slots", "repeating_slots", "slots"]
    for slot_type in slot_types:
        op.alter_column(slot_type,
                        column_name="application",
                        new_column_name="application_id")


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
