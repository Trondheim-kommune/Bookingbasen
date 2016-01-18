"""Create role and relationship

Revision ID: 14f3669b2884
Revises: 1e9953864388
Create Date: 2014-05-21 10:13:29.107112

"""

# revision identifiers, used by Alembic.
revision = '14f3669b2884'
down_revision = '1e9953864388'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
    )
    op.create_table('users_roles',
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('role_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.db_id']),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'])
    )


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
