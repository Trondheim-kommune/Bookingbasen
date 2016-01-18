"""creating unique constraint for name column for umbrella organisation

Revision ID: 560069e4e4fc
Revises: 198136299355
Create Date: 2014-04-14 08:35:55.634196

"""

# revision identifiers, used by Alembic.
revision = '560069e4e4fc'
down_revision = '198136299355'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint(                                                     
        "umbrella_organisation_unique_name_key",                                             
        "umbrella_organisations", 
        ["name"]
    ) 


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
