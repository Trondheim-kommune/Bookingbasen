"""Facility is published

Revision ID: 430e5b9bee56
Revises: 224bb149ff17
Create Date: 2014-04-07 12:44:33.761038

"""

# revision identifiers, used by Alembic.
revision = '430e5b9bee56'
down_revision = '224bb149ff17'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("facilities", sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("1")))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
