"""added_byomfattende_felt

Revision ID: d6c6cef2eb
Revises: 5616705b0022
Create Date: 2015-06-26 14:56:31.399142

"""

# revision identifiers, used by Alembic.
revision = 'd6c6cef2eb'
down_revision = '5616705b0022'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organisations', sa.Column('recruitment_area', sa.String(), nullable=True))

def downgrade():
    op.drop_column('organisations', 'recruitment_area')
