"""remove contact email

Revision ID: 2fb410522e9f
Revises: 430e5b9bee56
Create Date: 2014-05-28 12:36:53.597784

"""

# revision identifiers, used by Alembic.
revision = '2fb410522e9f'
down_revision = '430e5b9bee56'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("contact_persons", "email")


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
