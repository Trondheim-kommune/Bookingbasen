"""Invoice amount

Revision ID: 5099572b9811
Revises: 412efb4b1c45
Create Date: 2014-07-14 09:18:02.034419

"""

# revision identifiers, used by Alembic.
revision = '5099572b9811'
down_revision = '412efb4b1c45'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('applications', sa.Column('invoice_amount', sa.Integer(),
                                            nullable=True))


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
