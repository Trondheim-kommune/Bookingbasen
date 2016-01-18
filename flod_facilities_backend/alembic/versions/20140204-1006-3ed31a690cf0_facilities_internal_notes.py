"""facilities_internal_notes

Revision ID: 3ed31a690cf0
Revises: 19b609b20445
Create Date: 2014-02-04 10:06:56.994662

"""

# revision identifiers, used by Alembic.
revision = '3ed31a690cf0'
down_revision = '19b609b20445'

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.create_table('facilities_internal_notes',
    sa.Column('id', sa.Integer(), nullable=False), 
    sa.Column('facility_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('auth_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
	raise NotImplementedError('This application does not support downgrades.')
