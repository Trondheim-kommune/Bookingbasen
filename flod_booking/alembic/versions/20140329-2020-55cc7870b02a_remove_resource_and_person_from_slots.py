"""Remove resource and person from slots

Revision ID: 55cc7870b02a
Revises: 3b1769f1cfdb
Create Date: 2014-03-29 20:20:50.274118

"""

# revision identifiers, used by Alembic.
revision = '55cc7870b02a'
down_revision = '3b1769f1cfdb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("strotime_slots", "resource_id")
    op.drop_column("strotime_slots", "person_id")

    op.drop_column("repeating_slots", "resource_id")

    op.drop_column("slots", "resource_id")
    op.drop_column("slots", "person_id")
    op.drop_column("slots", "organisation_id")


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
