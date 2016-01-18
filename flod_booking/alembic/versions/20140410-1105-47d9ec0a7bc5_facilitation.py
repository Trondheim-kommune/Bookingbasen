"""facilitation

Revision ID: 47d9ec0a7bc5
Revises: 55cc7870b02a
Create Date: 2014-04-10 11:05:05.060080

"""

# revision identifiers, used by Alembic.
revision = '47d9ec0a7bc5'
down_revision = '55cc7870b02a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("applications", sa.Column('facilitation', sa.String()))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
