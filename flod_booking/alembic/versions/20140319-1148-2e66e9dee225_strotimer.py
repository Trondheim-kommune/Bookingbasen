"""Strotimer

Revision ID: 2e66e9dee225
Revises: 476eed020c40
Create Date: 2014-03-19 11:48:52.241100

"""

# revision identifiers, used by Alembic.
revision = '2e66e9dee225'
down_revision = '476eed020c40'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('strotime_slots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('resource_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),    
    sa.Column('status', sa.Enum('Granted', 'Denied', name='strotime_slot_status_types'),
              nullable=True),
    sa.Column('application', sa.Integer(), nullable=True),    
    sa.ForeignKeyConstraint(['application'], ['applications.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
