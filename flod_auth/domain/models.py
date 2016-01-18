# -*- coding: utf-8 -*-
import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime, Enum, Table, ForeignKey, PickleType
from sqlalchemy.orm import relationship

from database import Base


def enum(**kwenums):
    enums = dict((key, value) for key, value in kwenums.iteritems())
    reverse = dict((value, key) for key, value in kwenums.iteritems())
    enums['map'] = kwenums
    # reverse map
    enums['r_map'] = reverse
    return type('Enum', (), enums)


AuthenticationTypeEnum = enum(ACTIVE_DIRECTORY='active_directory',
                              ID_PORTEN='id_porten')

users_credentials = Table('users_credentials', Base.metadata,
                          Column('user_id', Integer, ForeignKey('user.db_id')),
                          Column('credential_id', Integer, ForeignKey('credential.db_id'))
)

users_roles = Table('users_roles', Base.metadata,
                    Column('user_id', Integer, ForeignKey('user.db_id')),
                    Column('role_id', Integer, ForeignKey('role.id')))


class User(Base):
    """ User class

    Attributes:
        db_id           Database id
        id              Used by external applications to refer to the user.
                        Typically a hash generated the first time the object is created.
        private_id      Unique user identifier, should not be exposed to external applications but can be queried
                        and modified. Can for example be a national identity number.
        person_id       The id of the associated person in flod_organisations, if existing.
        created_on      -
        auth_timestamp  Timestamp witch the authentication last authentication token was created
        credentials     -
        misc            Misc attributes as dict.
    """
    __tablename__ = 'user'
    db_id = Column(Integer, primary_key=True)
    id = Column(String, nullable=False, unique=True)
    authentication_type = Column(String, nullable=False)
    private_id = Column(String, nullable=False, unique=True)
    person_id = Column(Integer, unique=True)
    created_on = Column(DateTime(), nullable=False)
    auth_timestamp = Column(DateTime(), nullable=True)
    profile = relationship("Profile", uselist=False, backref="user")
    credentials = relationship("Credential", lazy=False, secondary=users_credentials)
    misc = Column(PickleType)
    roles = relationship("Role", lazy=False, secondary=users_roles)

    def __init__(self, private_id,
                 authentication_type=AuthenticationTypeEnum.ID_PORTEN):
        authentication_type_enum = AuthenticationTypeEnum.r_map.get(authentication_type)
        assert authentication_type_enum, \
            "Unknown authentication type '%s', should be one of %s." \
            % (authentication_type, ', '.join(AuthenticationTypeEnum.r_map))
        assert len(private_id) > 0
        self.authentication_type = authentication_type
        self.private_id = private_id
        self.created_on = datetime.datetime.now()
        self.id = hashlib.sha224(self.private_id + self.created_on.strftime("%Y%m%d%H%M%S%f")).hexdigest()
        self.renew_auth()
        self.misc = {}

    def renew_auth(self):
        self.auth_timestamp = datetime.datetime.now()


# These are the postgres enums
_authentication_type_enums = Enum(*AuthenticationTypeEnum.map.values(), name='authentication_type_enums')


class Credential(Base):
    """ Credentials which can be given to users

    Can alse be used to model credentials related  to resources. Resources objects found in flod applications like
    for example bookings, rooms or organisations.

    This object does not store uris to the resources, it is the application which has the responsibility to build those
    (to prevent having to migrate the saved ResourceCredentials when they "move" to other uris).

    Attributes:
        db_id        Database id
        id           The id of the credential, used by external applications to refer to the credential
        description  A human readable description of the credential
        resource_id   the id for the resource, e.g. facility, booking etc
    """
    __tablename__ = 'credential'
    credential_path = 'credential'
    db_id = Column(Integer, primary_key=True)
    id = Column(String, nullable=False, unique=True)
    description = Column(String)
    resource_id = Column(String)

    def __init__(self, credential_id, description, resource_id=None):
        assert len(credential_id) > 0
        self.id = credential_id
        self.description = description
        self.resource_id = resource_id

    @property
    def uri(self):
        return "%s/%s" % (self.credential_path, self.id)


class Profile(Base):
    """ Users profile information

    Attributes:
        db_id        Database id
        user_id      The id of the user owning this profile
        national_id_number
        active_directory_id
        first_name
        last_name
        email
        phone
    """
    __tablename__ = 'profile'
    db_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.db_id'))
    national_id_number = Column(String)
    active_directory_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)

    def full_name(self):
        first_name = self.first_name if self.first_name is not None else ""
        last_name = self.last_name if self.last_name is not None else ""
        full_name = " ".join([first_name, last_name]).strip()

        return full_name if full_name is not "" else self.active_directory_id if self.active_directory_id else self.user.id


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name
