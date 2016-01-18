# -*- coding: utf-8 -*-
from geoalchemy2.shape import from_shape, to_shape
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import (CheckConstraint, Column, ForeignKey, Integer, String,
                        Text, DateTime, Boolean)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE
from shapely.geometry import shape

from database import Base
from datetime import datetime


def convert_wkb_element_to_shape(geometry):
    if isinstance(geometry, WKBElement):
        return to_shape(geometry)
    else:
        return None


class Facility(Base):
    __tablename__ = 'facilities'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    pos = Column('geog', Geometry(geometry_type='POINT', srid=4326),
                 nullable=True)
    floor = Column(String(50), nullable=True)
    room = Column(String(50), nullable=True)
    images = relationship('Image', backref='facility', lazy=False)
    documents = relationship('Document', backref='facility', lazy=False)
    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    link = Column(String(200), nullable=True)
    contact_person = relationship(
        'ContactPerson', uselist=False, backref='facility', lazy=False)
    facility_type_id = Column(Integer, ForeignKey('facility_types.id'))
    facility_type = relationship('FacilityType', uselist=False, lazy=False)
    capacity = Column('capacity', Integer, CheckConstraint('capacity>-1'), nullable=True)
    short_code = Column(String(30))
    unit_number = Column(String(50))
    area = Column(Integer)
    conditions = Column(Text, nullable=True)
    unit_type_id = Column(Integer, ForeignKey('facility_unit_types.id'))
    unit_type = relationship('UnitType', uselist=False, lazy=False)
    district_id = Column(Integer, ForeignKey('districts.id'))
    district = relationship('District', uselist=False, lazy=False)
    unit_name = Column(String(255))
    unit_phone_number = Column(String(8))
    unit_email_address = Column(String(255))
    unit_leader_name = Column(String(255))
    address = Column(String(255))
    department_name = Column(String(255))
    amenities = Column(MutableDict.as_mutable(HSTORE))
    accessibility = Column(MutableDict.as_mutable(HSTORE))
    equipment = Column(MutableDict.as_mutable(HSTORE))
    suitability = Column(MutableDict.as_mutable(HSTORE))
    facilitators = Column(MutableDict.as_mutable(HSTORE))
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_published = Column(Boolean, nullable=False, default=True)

    def __init__(self, name, **kwargs):
        assert len(name) > 0
        self.name = name
        self.set_position(kwargs.get("position", None))
        self.floor = kwargs.get('floor', None)
        self.room = kwargs.get('room', None)
        self.short_description = kwargs.get('short_description', None)
        self.description = kwargs.get('description', None)
        self.link = kwargs.get('link', None)
        self.contact_person = kwargs.get('contact_person', None)
        self.facility_type = kwargs.get('facility_type', None)
        self.capacity = kwargs.get('capacity', None)
        self.short_code = kwargs.get('short_code', None)
        self.unit_number = kwargs.get('unit_number', None)
        self.area = kwargs.get('area', None)
        self.conditions = kwargs.get('conditions', None)
        self.unit_name = kwargs.get('unit_name', None)
        self.unit_type = kwargs.get('unit_type', None)
        self.unit_phone_number = kwargs.get('unit_phone_number', None)
        self.unit_email_address = kwargs.get('unit_email_address', None)
        self.unit_leader_name = kwargs.get('unit_leader_name', None)
        self.address = kwargs.get("address", None)
        self.department_name = kwargs.get('department_name', None)
        self.amenities = {}
        self.accessibility = {}
        self.equipment = {}
        self.suitability = {}
        self.facilitators = {}
        self.is_deleted = kwargs.get('is_deleted', False)
        self.is_published = kwargs.get('is_published', True)

    @property
    def position(self):
        return convert_wkb_element_to_shape(self.pos)

    def set_position(self, position):
        if position:
            self.pos = from_shape(position, srid=4326)
        else:
            self.pos = None

    @property
    def uri(self):
        return '/facilities/%s' % self.id


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    url = Column(String(150), nullable=False)
    title = Column(String(50), nullable=False)
    filename = Column(String(50), nullable=False)
    storage_backend = Column(String(50), nullable=False)

    def __init__(self, facility, url, title, filename, storage_backend):
        self.facility = facility
        self.url = url
        self.title = title
        self.filename = filename,
        self.storage_backend = storage_backend


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    url = Column(String(150), nullable=False)
    title = Column(String(50), nullable=False)
    filename = Column(String(50), nullable=False)
    storage_backend = Column(String(50), nullable=False)

    def __init__(self, facility, url, title, filename, storage_backend):
        self.facility = facility
        self.url = url
        self.title = title
        self.filename = filename
        self.storage_backend = storage_backend


class ContactPerson(Base):
    __tablename__ = 'contact_persons'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    name = Column(String(50), nullable=False)
    phone_number = Column(String(8))

    def __init__(self, name, **kwargs):
        self.name = name
        self.phone_number = kwargs.get("phone_number", None)


class FacilityType(Base):
    __tablename__ = 'facility_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class UnitType(Base):
    __tablename__ = 'facility_unit_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    geom = Column('geog', Geometry(geometry_type='POLYGON', srid=4326),
                  nullable=False)

    def __init__(self, geojson_data):
        self.name = geojson_data.get("properties").get("name")
        self.geom = from_shape(shape(geojson_data.get("geometry")),
                               srid=4326)

    @property
    def geometry(self):
        return convert_wkb_element_to_shape(self.geom)


class FacilityInternalNote(Base):
    __tablename__ = 'facilities_internal_notes'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    facility = relationship("Facility", lazy=False)
    text = Column(String, nullable=False)
    create_time = Column(DateTime, nullable=False)
    auth_id = Column(String, nullable=False)

    def __init__(self, facility, text, auth_id):
        self.facility = facility
        self.text = text
        self.create_time = datetime.now()
        self.auth_id = auth_id
