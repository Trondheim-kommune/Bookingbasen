"""facility_is_deleted

Revision ID: 224bb149ff17
Revises: 3ed31a690cf0
Create Date: 2014-04-03 11:11:27.705401

"""

# revision identifiers, used by Alembic.
revision = '224bb149ff17'
down_revision = '3ed31a690cf0'

from alembic import op
import sqlalchemy as sa

def upgrade():
#    op.add_column("facilities", sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False))
    op.add_column("facilities", sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("0")))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
