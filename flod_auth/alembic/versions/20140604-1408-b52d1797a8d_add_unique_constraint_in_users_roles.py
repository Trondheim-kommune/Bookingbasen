"""Add unique constraint in users_roles

Revision ID: b52d1797a8d
Revises: 14f3669b2884
Create Date: 2014-06-04 14:08:05.902527

"""

# revision identifiers, used by Alembic.
revision = 'b52d1797a8d'
down_revision = '14f3669b2884'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint('user_id_role_id_unique_key', 'users_roles',
                                ['user_id', 'role_id'])


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
