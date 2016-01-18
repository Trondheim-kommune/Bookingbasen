# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.orm import relationship

from database import Base

def enum(**kwenums):
    enums = dict((key, value) for key, value in kwenums.iteritems())
    reverse = dict((value, key) for key, value in kwenums.iteritems())
    enums['map'] = kwenums
    # reverse map
    enums['r_map'] = reverse
    return type('Enum', (), enums)

person_org_association_role_table = Table('person_org_association_roles', Base.metadata,
                                          Column('org_person_association_id', Integer,
                                                 ForeignKey('organisation_person_associations.id')),
                                          Column('role_association_id', Integer,
                                                 ForeignKey('person_org_assoc_roles.id'))
)


class OrganisationPersonAssociation(Base):
    __tablename__ = 'organisation_person_associations'
    id = Column(Integer, primary_key=True)
    organisation_id = Column(Integer, ForeignKey('organisations.id'))
    person_id = Column(Integer, ForeignKey('persons.id'))
    from_brreg = Column(Boolean, nullable=True)
    person = relationship("Person", backref="organisations")
    roles = relationship("PersonOrgAssociationRole", secondary=person_org_association_role_table, lazy=False)


    def __init__(self, person, from_brreg=None, roles=()):
        self.person = person
        self.from_brreg = from_brreg
        for role in roles:
            self.roles.append(role)


class PersonOrgAssociationRole(Base):
    __tablename__ = 'person_org_assoc_roles'

    id = Column(Integer(), primary_key=True)
    role = Column(String(200))

    def __init__(self, role):
        assert role
        self.role = role


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer(), primary_key=True)
    address_line = Column(String(200))
    postal_code = Column(String(4))
    postal_city = Column(String(100))

    def __init__(self, address_line=None, postal_code=None, postal_city=None):
        self.address_line = address_line
        self.postal_code = postal_code
        self.postal_city = postal_city


organisation_brreg_activity_code_association_table = Table('organisation_brreg_activities', Base.metadata,
                                                           Column('org_id', Integer, ForeignKey('organisations.id')),
                                                           Column('brreg_code_list_id', Integer,
                                                                  ForeignKey('brreg_activity_codes.id'))
)

organisation_flod_activity_type_association_table = Table('organisation_flod_activity_types', Base.metadata,
                                                          Column('org_id', Integer, ForeignKey('organisations.id')),
                                                          Column('flod_type_list_id', Integer,
                                                                 ForeignKey('flod_activity_type.id'))
)


class Organisation(Base):
    __tablename__ = 'organisations'

    id = Column(Integer(), primary_key=True)
    org_number = Column(String(10))
    name = Column(String(200))
    org_form = Column(String(50))

    email_address = Column(String(150))
    local_email_address = Column(String(150))
    phone_number = Column(String(12))
    telefax_number = Column(String(12))
    url = Column(String(255))

    account_number = Column(String(15))

    business_address_id = Column(Integer, ForeignKey('addresses.id'))
    business_address = relationship('Address', lazy=False, uselist=False,
                                    primaryjoin="Organisation.business_address_id == Address.id")

    postal_address_id = Column(Integer, ForeignKey('addresses.id'))
    postal_address = relationship('Address', lazy=False, uselist=False,
                                  primaryjoin="Organisation.postal_address_id == Address.id")


    people = relationship("OrganisationPersonAssociation", lazy=False, backref="organisation",
                          cascade="all, delete, delete-orphan")

    brreg_activity_codes = relationship("BrregActivityCode",
                                        lazy=False,
                                        secondary=organisation_brreg_activity_code_association_table,
                                        backref="organisations")


    tilholdssted_address_id = Column(Integer, ForeignKey('addresses.id'))
    tilholdssted_address = relationship('Address', lazy=False, uselist=False,
                                        primaryjoin="Organisation.tilholdssted_address_id == Address.id")


    # Trondheim kommune specific fields

    flod_activity_types = relationship("FlodActivityType",
                                       lazy=False,
                                       secondary=organisation_flod_activity_type_association_table,
                                       backref="organisations")

    num_members_b20 = Column(Integer())
    num_members = Column(Integer())
    description = Column(Text())
    area = Column(Integer())
    recruitment_area = Column(Integer())
    registered_tkn = Column(Boolean)
    relevant_tkn = Column(Boolean)

    # True if user has consented to the org being publicly viewable
    is_public = Column(Boolean)

    is_deleted = Column(Boolean, nullable=False, default=False)

    def __init__(self, org_number=None, name=None, **kwargs):
        if org_number:
            self.org_number = org_number
        if name:
            self.name = name
        self.org_form = kwargs.get("org_form", None)

        self.email_address = kwargs.get("email_address", None)
        self.local_email_address = kwargs.get("local_email_address", None)
        self.phone_number = kwargs.get("phone_number", None)
        self.telefax_number = kwargs.get("telefax_number", None)
        self.url = kwargs.get("url", None)

        self.account_number = kwargs.get("account_number", None)

        if kwargs.get("postal_address"):
            self.postal_address = kwargs.get("postal_address")
        if kwargs.get("business_address"):
            self.business_address = kwargs.get("business_address")
        if kwargs.get("tilholdssted_address"):
            self.tilholdssted_address = kwargs.get("tilholdssted_address")

        self.type_organisation = kwargs.get("type_organisation", None)
        self.num_members_b20 = kwargs.get("num_members_b20", None)
        self.num_members = kwargs.get("num_members", None)
        self.description = kwargs.get("description", None)
        self.area = kwargs.get("area", 0)
        self.recruitment_area = kwargs.get("recruitment_area", 0)
        self.registered_tkn = kwargs.get("registered_tkn", False)
        self.relevant_tkn = kwargs.get("relevant_tkn", False)
        self.is_public = kwargs.get("is_public", False)

    @property
    def brreg_activity_code(self):
        return [x.code for x in self.brreg_activity_codes]

    @property
    def persons(self):
        result = []
        for person_assoc in self.people:
            person_assoc.person.from_brreg = person_assoc.from_brreg
            result.append(person_assoc.person)
        return result

    @property
    def flod_activity_type(self):
        return [x.id for x in self.flod_activity_types]

    def add_person_association(self, person_association):
        self.people.append(person_association)

    def add_brreg_activity_code(self, activity_code):
        brreg_activity_code = BrregActivityCode.query.filter(BrregActivityCode.code == activity_code).one()
        self.brreg_activity_codes.append(brreg_activity_code)

    def add_flod_activity_type(self, activity_types):
        for act_type in activity_types:
            flod_activity_type = FlodActivityType.query.filter(FlodActivityType.id == act_type).one()
            if flod_activity_type.brreg_activity_code not in self.brreg_activity_codes:
                raise ValueError('Invalid activity code')
            self.flod_activity_types.append(flod_activity_type)

    @property
    def uri(self):
        return "/organisations/%s" % self.id


person_status_enums = Enum("unregistered", "registered", name="person_status_enums")


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(200), nullable=True)
    last_name = Column(String(200), nullable=True)
    national_identity_number = Column(String(11), unique=True)
    status = Column(person_status_enums)
    address_line = Column(String(200), nullable=True)
    postal_code = Column(String(4), nullable=True)
    postal_city = Column(String(100), nullable=True)
    email_address = Column(String(150), unique=True)  # nullable=False
    phone_number = Column(String(12), nullable=True)


    @property
    def uri(self):
        return "/persons/%s" % self.id

    def __init__(self, national_identity_number, **kwargs):
        assert national_identity_number
        self.national_identity_number = national_identity_number
        self.first_name = kwargs.get("first_name", None)
        self.last_name = kwargs.get("last_name", None)
        self.status = kwargs.get("status", "unregistered")
        self.address_line = kwargs.get("address_line", None)
        self.postal_code = kwargs.get("postal_code", None)
        self.postal_city = kwargs.get("postal_city", None)
        self.email_address = kwargs.get("email_address", None)
        self.phone_number = kwargs.get("phone_number", None)


class PersonBrregAddress(Base):
    __tablename__ = 'person_brreg_address'

    id = Column(Integer, primary_key=True)
    address_line = Column(String(200), nullable=True)
    postal_code = Column(String(4), nullable=True)
    postal_city = Column(String(100), nullable=True)

    def __init__(self, address_line=None, postal_code=None, postal_city=None):
        self.address_line = address_line
        self.postal_code = postal_code
        self.postal_city = postal_city


class BrregActivityCode(Base):
    __tablename__ = 'brreg_activity_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
    flod_activity_types = relationship("FlodActivityType", backref="brreg_activity_code")

    def __init__(self, code, description):
        self.code = code
        self.description = description


class FlodActivityType(Base):
    __tablename__ = 'flod_activity_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    brreg_activity_code_id = Column(Integer, ForeignKey('brreg_activity_codes.id'))

    def __init__(self, name, brreg_activity_code):
        self.name = name
        self.brreg_activity_code = brreg_activity_code


class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


umbrella_organisation_person_association_table = \
    Table('umbrella_organisation_person_associations', Base.metadata,
          #Column('id', Integer, primary_key=True),
          Column('umbrella_organisation_id', Integer, ForeignKey('umbrella_organisations.id')),
          Column('person_id', Integer, ForeignKey('persons.id')))

class UmbrellaOrgMemberOrgAssociation(Base):
    __tablename__ = 'umbrella_organisation_oraganisation_associations'
    id = Column(Integer(), primary_key=True)
    organisation_id = Column(Integer, ForeignKey('organisations.id'))
    umbrella_organisation_id = Column(Integer, ForeignKey('umbrella_organisations.id'))
    umbrella_organisation = relationship("UmbrellaOrganisation")
    organisation = relationship("Organisation", backref="organisations")

    def __init__(self, umbrella_organisation, organisation):
        self.umbrella_organisation = umbrella_organisation
        self.organisation = organisation

class UmbrellaOrganisation(Base):
    __tablename__ = 'umbrella_organisations'

    id = Column(Integer(), primary_key=True)
    name = Column(String(200), unique=True)
    persons = relationship("Person",
                           order_by="Person.id",
                           secondary="umbrella_organisation_person_associations",
                           lazy=False,
                           backref="umbrella_organisations")
    organisations = relationship("Organisation",
                                 order_by="Organisation.id",
                                 secondary="umbrella_organisation_oraganisation_associations",
                                 lazy=False,
                                 backref="umbrella_organisations")
    is_deleted = Column(Boolean, nullable=False, default=False)

    def __init__(self, name):
        self.name = name
        self.persons = []
        self.organisations = []

    def add_person(self, person):
        self.persons.append(person)

    def add_organisation(self, organisation):
        self.organisations.append(organisation)

    def remove_person(self, person):
        self.persons.remove(person)

    def remove_organisation(self, organisation):
        self.organisations.remove(organisation)

    @property
    def uri(self):
        return '/umbrella_organisations/%s' % self.id

class OrganisationInternalNote(Base):
    __tablename__ = 'organisations_internal_notes'
    id = Column(Integer, primary_key=True)
    organisation_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    organisation = relationship("Organisation", lazy=False)
    text = Column(String, nullable=False)
    create_time = Column(DateTime, nullable=False)
    auth_id = Column(String, nullable=False)

    def __init__(self, organisation, text, auth_id):
        self.organisation = organisation
        self.text = text
        self.create_time = datetime.now()
        self.auth_id = auth_id
