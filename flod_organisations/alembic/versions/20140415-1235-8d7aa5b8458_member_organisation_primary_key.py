"""Member organisation primary key

Revision ID: 8d7aa5b8458
Revises: 560069e4e4fc
Create Date: 2014-04-15 12:35:36.348480

"""

# revision identifiers, used by Alembic.
revision = '8d7aa5b8458'
down_revision = '560069e4e4fc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("umbrella_organisation_oraganisation_associations", sa.Column('id', sa.Integer(), primary_key = True))
    op.create_unique_constraint(
        "umbrella_organisation_oraganisation_associations_unique_key",
        "umbrella_organisation_oraganisation_associations",
        ["organisation_id", "umbrella_organisation_id"]
    )

def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
