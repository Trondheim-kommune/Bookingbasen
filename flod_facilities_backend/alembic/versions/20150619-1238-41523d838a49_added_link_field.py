"""added_link_field

Revision ID: 41523d838a49
Revises: 30e18bf0fa87
Create Date: 2015-06-19 12:38:37.565723

"""

# revision identifiers, used by Alembic.
revision = '41523d838a49'
down_revision = '30e18bf0fa87'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('facilities', sa.Column('link', sa.String(length=200), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('facilities', 'link')
    ### end Alembic commands ###
