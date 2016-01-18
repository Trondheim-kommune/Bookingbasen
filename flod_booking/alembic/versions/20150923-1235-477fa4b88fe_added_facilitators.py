"""added facilitators

Revision ID: 477fa4b88fe
Revises: 41e40fd528c6
Create Date: 2015-09-23 12:35:35.639645

"""

# revision identifiers, used by Alembic.
revision = '477fa4b88fe'
down_revision = '41e40fd528c6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('applications', sa.Column('facilitators', postgresql.HSTORE(), nullable=True))
    op.add_column('applications', sa.Column('requested_facilitators', postgresql.HSTORE(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('applications', 'requested_facilitators')
    op.drop_column('applications', 'facilitators')
    ### end Alembic commands ###
