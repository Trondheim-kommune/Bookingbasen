"""Application message

Revision ID: 294279d0f1ea
Revises: 4efdbda3b553
Create Date: 2014-03-27 08:16:34.189360

"""

# revision identifiers, used by Alembic.
revision = '294279d0f1ea'
down_revision = '4efdbda3b553'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("applications", sa.Column('message', sa.String()))

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
