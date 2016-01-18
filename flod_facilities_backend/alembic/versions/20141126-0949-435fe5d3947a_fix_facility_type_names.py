# -*- coding: utf-8 -*-
"""fix facility type names

Revision ID: 435fe5d3947a
Revises: 2fb410522e9f
Create Date: 2014-11-26 09:49:28.682603

"""

# revision identifiers, used by Alembic.
revision = '435fe5d3947a'
down_revision = '2fb410522e9f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String



def upgrade():
    account = table('facility_types',
                    column('name', String)
                )

    changes = [
        (u'Isidrettshall (ishall/skøytebane)', u'Ishall'),
        (u'Utendørs friidrettsanlegg', u'Friidrettsanlegg'),
        (u'Utendørs skianlegg', u'Skianlegg') ]

    for (old, new) in changes:
        op.execute(
            account.update().\
            where(account.c.name==op.inline_literal(old)).\
            values({'name':op.inline_literal(new)})
        )

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
