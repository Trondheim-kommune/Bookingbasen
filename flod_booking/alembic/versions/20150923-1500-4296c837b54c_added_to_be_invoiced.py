"""empty message

Revision ID: 4296c837b54c
Revises: 3000bfc6da03
Create Date: 2015-09-22 15:00:51.644676

"""

# revision identifiers, used by Alembic.
revision = '4296c837b54c'
down_revision = '302c467502a1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('applications', sa.Column('to_be_invoiced', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('applications', 'to_be_invoiced')
    ### end Alembic commands ###
