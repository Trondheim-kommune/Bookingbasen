"""Rammetid

Revision ID: 3ad3fdc028ea
Revises: 55cc7870b02a
Create Date: 2014-04-23 13:02:01.385878

"""

# revision identifiers, used by Alembic.
revision = '3ad3fdc028ea'
down_revision = '483e5e40b48d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('umbrella_organisations',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('uri', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('uri')
    )

    op.create_table('rammetid',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('umbrella_organisation_id', sa.Integer(), nullable=True),
                    sa.Column('resource_id', sa.Integer(), nullable=False),
                    sa.Column('status',
                              sa.Enum('Processing', 'Finished', name='rammetid_status_types'),
                              nullable=True),
                    sa.Column('create_time', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['umbrella_organisation_id'], ['umbrella_organisations.id']),
                    sa.ForeignKeyConstraint(['resource_id'], ['resources.id']),
                    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('rammetid_slots',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('week_day', sa.Integer(), nullable=False),
                    sa.Column('start_date', sa.Date(), nullable=False),
                    sa.Column('end_date', sa.Date(), nullable=False),
                    sa.Column('start_time', sa.Time(), nullable=False),
                    sa.Column('end_time', sa.Time(), nullable=False),
                    sa.Column('rammetid_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['rammetid_id'], ['rammetid.id']),
                    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
