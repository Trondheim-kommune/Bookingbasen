"""Add is_public field to organisation

Revision ID: 24ab9976c0a1
Revises: 19fb74ccad07
Create Date: 2014-06-17 09:55:32.652175

"""

# revision identifiers, used by Alembic.
revision = '24ab9976c0a1'
down_revision = '19fb74ccad07'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("organisations",
                  sa.Column('is_public', sa.Boolean(), nullable=False,
                            server_default=sa.schema.DefaultClause("0")))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
