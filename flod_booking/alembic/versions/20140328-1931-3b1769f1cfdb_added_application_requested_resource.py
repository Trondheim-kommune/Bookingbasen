"""Added application requested_resource

Revision ID: 3b1769f1cfdb
Revises: 294279d0f1ea
Create Date: 2014-03-28 19:31:55.435603

"""

# revision identifiers, used by Alembic.
revision = '3b1769f1cfdb'
down_revision = '294279d0f1ea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey

def upgrade():
    connection = op.get_bind()

    # Add the column and allow it to be nullable
    op.add_column('applications',
                  sa.Column('requested_resource_id', sa.Integer(),
                            ForeignKey("resources.id"),
                            nullable=True))

    try:
        # Migrate the existing data (assign resource_id to the new field)
        applications = sa.Table("applications", sa.MetaData(),
                                sa.Column('id', sa.Integer, primary_key=True),
                                sa.Column('resource_id', sa.Integer, nullable=False),
                                sa.Column('requested_resource_id', sa.Integer, nullable=True),
                                autoload=True,
                                autoload_with=connection.engine)

        for application in connection.execute(applications.select()):
            connection.execute(
                applications.update().where(
                    applications.c.id == application.id
                ).values(
                    { "requested_resource_id" : application.resource_id }
                )
            )

        # now that all applications have a valid requested_resource_id
        # we make it non-nullable.
        op.alter_column('applications', "requested_resource_id", nullable=False)
    except:
        pass


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
