# -*- coding: utf-8 -*-
"""added_districts_table

Revision ID: 5616705b0022
Revises: 52923cf8bab3
Create Date: 2015-06-26 12:46:49.023334

"""

# revision identifiers, used by Alembic.
revision = '5616705b0022'
down_revision = '424f4e48b5ad'

from alembic import op
from sqlalchemy import *


def upgrade():

    district_table = op.create_table('districts',
                                     Column('id', Integer(), nullable=False),
                                     Column('name', String, nullable=False)
    )


    op.bulk_insert(district_table,
                   [
                       {"id": 0,"name": "Hele Trondheim"},
                       {"id": 1,"name": "Trondheim Sentrum"},
                       {"id": 2,"name": "Trondheim Vest"},
                       {"id": 3,"name": "Trondheim Øst"},
                       {"id": 4,"name": "Trondheim Sør"}
                   ]
    )


def downgrade():
    op.drop_table('districts')
