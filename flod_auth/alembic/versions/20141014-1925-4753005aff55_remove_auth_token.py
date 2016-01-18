"""remove auth_token

Revision ID: 4753005aff55
Revises: b52d1797a8d
Create Date: 2014-10-14 19:25:01.267434

"""

# revision identifiers, used by Alembic.
revision = '4753005aff55'
down_revision = 'b52d1797a8d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('user', 'auth_token')



def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
