# -*- coding: utf-8 -*-
"""BOOK-131 Noark 5 documents will temporarily be saved in flod (the integration point, FeSak, is not ready to receive them)

Revision ID: 483e5e40b48d
Revises: 47d9ec0a7bc5
Create Date: 2014-03-07 14:14:59.182049

"""

# revision identifiers, used by Alembic.
revision = '483e5e40b48d'
down_revision = '47d9ec0a7bc5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('fesak_sak',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('application_id', sa.Integer(), nullable=False),
                    sa.Column('saksnummer', sa.String(), nullable=False),
                    sa.Column('ws_header', sa.String(), nullable=False),
                    sa.Column('ws_sak', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
                    sa.UniqueConstraint('application_id')
    )
    op.create_table('fesak_journalpost',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('fesak_sak_id', sa.Integer(), nullable=False),
                    sa.Column('ws_header', sa.String(), nullable=False),
                    sa.Column('ws_journalpost', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['fesak_sak_id'], ['fesak_sak.id'], ),
    )



def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
