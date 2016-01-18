# -*- coding: utf-8 -*-
"""Initial conversion from sqlalchemy create all to alembic

Revision ID: 33134fcc7129
Revises: None
Create Date: 2014-01-10 12:47:31.546664

"""

# revision identifiers, used by Alembic.
from geoalchemy2 import Geometry

revision = '33134fcc7129'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('districts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('geog', Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('facility_unit_types',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('facility_types',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('facilities',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('geog', Geometry(geometry_type='POINT', srid=4326), nullable=True),
                    sa.Column('floor', sa.String(length=50), nullable=True),
                    sa.Column('room', sa.String(length=50), nullable=True),
                    sa.Column('short_description', sa.Text(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('facility_type_id', sa.Integer(), nullable=True),
                    sa.Column('capacity', sa.Integer(), nullable=True),
                    sa.Column('short_code', sa.String(length=30), nullable=True),
                    sa.Column('unit_number', sa.String(length=50), nullable=True),
                    sa.Column('area', sa.Integer(), nullable=True),
                    sa.Column('conditions', sa.Text(), nullable=True),
                    sa.Column('unit_type_id', sa.Integer(), nullable=True),
                    sa.Column('unit_name', sa.String(length=255), nullable=True),
                    sa.Column('unit_phone_number', sa.String(length=8), nullable=True),
                    sa.Column('unit_email_address', sa.String(length=255), nullable=True),
                    sa.Column('unit_leader_name', sa.String(length=255), nullable=True),
                    sa.Column('address', sa.String(length=255), nullable=True),
                    sa.Column('department_name', sa.String(length=255), nullable=True),
                    sa.Column('amenities', postgresql.HSTORE(), nullable=True),
                    sa.Column('accessibility', postgresql.HSTORE(), nullable=True),
                    sa.Column('district', postgresql.HSTORE(), nullable=True),
                    sa.Column('district_id', sa.Integer, nullable=True),
                    sa.Column('equipment', postgresql.HSTORE(), nullable=True),
                    sa.Column('suitability', postgresql.HSTORE(), nullable=True),
                    sa.ForeignKeyConstraint(['facility_type_id'], ['facility_types.id'], ),
                    sa.ForeignKeyConstraint(['unit_type_id'], ['facility_unit_types.id'], ),
                    sa.ForeignKeyConstraint(['district_id'], ['districts.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    # OBS: sqlalchemy checkconstraint do not seem to be detected by alembics --autogenerate
    op.create_check_constraint(
        "ck_is_positive_or_0_capacity",
        'facilities',
        'capacity>-1'
    )
    op.create_table('images',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('facility_id', sa.Integer(), nullable=True),
                    sa.Column('url', sa.String(length=150), nullable=False),
                    sa.Column('title', sa.String(length=50), nullable=False),
                    sa.Column('filename', sa.String(length=50), nullable=False),
                    sa.Column('storage_backend', sa.String(length=50), nullable=False),
                    sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('documents',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('facility_id', sa.Integer(), nullable=True),
                    sa.Column('url', sa.String(length=150), nullable=False),
                    sa.Column('title', sa.String(length=50), nullable=False),
                    sa.Column('filename', sa.String(length=50), nullable=False),
                    sa.Column('storage_backend', sa.String(length=50), nullable=False),
                    sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contact_persons',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('facility_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('phone_number', sa.String(length=8), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['facility_id'], ['facilities.id'], ),
                    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    raise NotImplementedError('This application does not support downgrades.')
