"""Delete umbrella organisation

Revision ID: 19fb74ccad07
Revises: 8d7aa5b8458
Create Date: 2014-04-16 13:30:22.367009

"""

# revision identifiers, used by Alembic.
revision = '19fb74ccad07'
down_revision = '8d7aa5b8458'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("umbrella_organisations", sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("0")))

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
