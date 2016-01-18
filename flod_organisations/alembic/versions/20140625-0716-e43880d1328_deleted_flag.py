"""Deleted flag

Revision ID: e43880d1328
Revises: 24ab9976c0a1
Create Date: 2014-06-25 07:16:08.494675

"""

# revision identifiers, used by Alembic.
revision = 'e43880d1328'
down_revision = '24ab9976c0a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("organisations", sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("0")))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
