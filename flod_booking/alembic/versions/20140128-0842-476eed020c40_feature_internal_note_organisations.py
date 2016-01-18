"""FEATURE: Internal note organisations

Revision ID: 476eed020c40
Revises: 1b2a8e1a4d45
Create Date: 2014-01-28 08:42:50.178186

"""

# revision identifiers, used by Alembic.
revision = '476eed020c40'
down_revision = '1b2a8e1a4d45'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.create_table('organisations_internal_notes',
    sa.Column('id', sa.Integer(), nullable=False), 
    sa.Column('organisation_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('auth_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
