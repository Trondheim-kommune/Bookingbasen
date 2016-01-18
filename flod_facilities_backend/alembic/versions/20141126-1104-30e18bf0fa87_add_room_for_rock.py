# -*- coding: utf-8 -*-
"""add room for rock

Revision ID: 30e18bf0fa87
Revises: 435fe5d3947a
Create Date: 2014-11-26 11:04:01.806539

"""

# revision identifiers, used by Alembic.
revision = '30e18bf0fa87'
down_revision = '435fe5d3947a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String

def upgrade():
    facility_types_table = table('facility_types',
                                 column('name', String)
    )
    op.bulk_insert(
        facility_types_table,
        [
            {"name": u'Øvingsrom for band'},
        ]
    )


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
