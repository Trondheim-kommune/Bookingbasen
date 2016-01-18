"""is arrangement

Revision ID: 436f5bd9fd4
Revises: 3ad3fdc028ea
Create Date: 2014-05-21 07:51:47.872929

"""

# revision identifiers, used by Alembic.
revision = '436f5bd9fd4'
down_revision = '3ad3fdc028ea'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("applications", sa.Column('is_arrangement', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("0")))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
