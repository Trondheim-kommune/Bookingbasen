# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE

from database import Base


class BookingDomainException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "Message: %s" % self.message


def check_dates_are_open_interval(start_date, end_date):
    if not (end_date is None or start_date <= end_date):
        raise BookingDomainException(u"Sluttdato er før startdato.")


def check_dates_are_closed_interval(start_date, end_date):
    if not (start_date <= end_date):
        raise BookingDomainException(u"Sluttdato er før startdato.")


def check_start_time_before_end_time(start_time, end_time):
    if not start_time <= end_time:
        raise BookingDomainException(
            u"Starttidspunkt må være før sluttidspunkt.")


def check_iso_week_day(week_day):
    if week_day < 1 or week_day > 7:
        raise BookingDomainException(u"Ugyldig ukenummer: %d" % week_day)


class UriResource(object):
    id = Column(Integer, primary_key=True)
    uri = Column(String(255), nullable=False, unique=True)

    def __init__(self, uri):
        assert (uri is not None)
        assert (len(uri) > 0)
        self.uri = uri


class Resource(UriResource, Base):
    __tablename__ = 'resources'
    auto_approval_allowed = Column(Boolean, nullable=False, default=False)
    single_booking_allowed = Column(Boolean, nullable=False, default=False)
    repeating_booking_allowed = Column(Boolean, nullable=False, default=False)

    def __init__(self, uri):
        UriResource.__init__(self, uri)
        self.auto_approval_allowed = False
        self.single_booking_allowed = False
        self.repeating_booking_allowed = False


class Person(UriResource, Base):
    __tablename__ = 'persons'


class Organisation(UriResource, Base):
    __tablename__ = 'organisations'


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


application_status_enums = Enum("Pending", "Processing", "Granted", "Denied",
                                name="application_status_types")


class Slot(Base):
    __tablename__ = 'slots'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"),
                            nullable=False)
    application = relationship("Application", lazy=False)

    def __init__(self, start_time, end_time, application):
        assert (application is not None)
        check_start_time_before_end_time(start_time, end_time)

        self.start_time = start_time
        self.end_time = end_time
        self.application = application
        self.application_id = application.id


class StrotimeSlot(Base):
    __tablename__ = 'strotime_slots'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"),
                            nullable=False)
    application = relationship("Application", lazy=False)

    def __init__(self, start_time, end_time, application):
        assert (application is not None)
        check_start_time_before_end_time(start_time, end_time)
        self.start_time = start_time
        self.end_time = end_time
        self.application = application


class SlotRequest(Base):
    __tablename__ = 'slot_requests'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"),
                            nullable=False)
    application = relationship("Application", lazy=False)

    def __init__(self, start_time, end_time):
        check_start_time_before_end_time(start_time, end_time)

        self.start_time = start_time
        self.end_time = end_time


class RepeatingSlot(Base):
    __tablename__ = 'repeating_slots'
    id = Column(Integer, primary_key=True)
    week_day = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"),
                            nullable=False)
    application = relationship("Application", lazy=False)

    def __init__(self,
                 application,
                 week_day,
                 start_date, end_date,
                 start_time, end_time):
        check_dates_are_closed_interval(start_date, end_date)
        check_start_time_before_end_time(start_time, end_time)
        check_iso_week_day(week_day)

        self.application = application
        self.week_day = week_day
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time


class RepeatingSlotRequest(Base):
    __tablename__ = 'repeating_slot_requests'
    id = Column(Integer, primary_key=True)
    week_day = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"),
                            nullable=False)
    application = relationship("Application", lazy=False)

    def __init__(self,
                 week_day,
                 start_date, end_date,
                 start_time, end_time):
        check_dates_are_closed_interval(start_date, end_date)
        check_start_time_before_end_time(start_time, end_time)
        check_iso_week_day(week_day)

        self.week_day = week_day
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time


class WeeklyBlockedTime(Base):
    __tablename__ = "weekly_blocked_times"
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    resource = relationship("Resource", lazy=False)
    week_day = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    note = Column(String, nullable=True)

    def __init__(self, resource, week_day, start_date, end_date, start_time, end_time, note):
        check_dates_are_open_interval(start_date, end_date)
        check_start_time_before_end_time(start_time, end_time)
        check_iso_week_day(week_day)

        self.resource = resource
        self.week_day = week_day
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.note = note


class BlockedTimeInterval(Base):
    __tablename__ = "blocked_time_intervals"
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    resource = relationship("Resource", lazy=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    note = Column(String, nullable=True)

    def __init__(self, resource, start_time, end_time, note):
        check_start_time_before_end_time(start_time, end_time)

        self.resource = resource
        self.start_time = start_time
        self.end_time = end_time
        self.note = note


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    person = relationship("Person", lazy=False)
    organisation_id = Column(Integer, ForeignKey("organisations.id"))
    organisation = relationship("Organisation", lazy=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    resource = relationship("Resource", lazy=False,
                            foreign_keys="Application.resource_id")
    requested_resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    requested_resource = relationship("Resource", lazy=False,
                                      foreign_keys="Application.requested_resource_id")
    text = Column(String, nullable=False)
    facilitation = Column(String)
    requested_repeating_slots = relationship("RepeatingSlotRequest", lazy=False, cascade="all, delete-orphan",
                                             passive_deletes=True)
    requested_single_slots = relationship("SlotRequest", lazy=False, cascade="all, delete-orphan",
                                          passive_deletes=True)
    status = Column(application_status_enums)
    application_time = Column(DateTime, nullable=False, default=datetime.now())
    repeating_slots = relationship("RepeatingSlot", lazy=False, cascade="all, delete-orphan",
                                   passive_deletes=True)
    single_slots = relationship("Slot", lazy=False, cascade="all, delete-orphan",
                                passive_deletes=True)
    strotime_slots = relationship("StrotimeSlot", lazy=False, cascade="all, delete-orphan",
                                  passive_deletes=True)
    message = Column(String)
    is_arrangement = Column(Boolean, nullable=False, default=False)
    invoice_amount = Column(Integer, nullable=True)
    to_be_invoiced = Column(Boolean, nullable=True, default=False)
    requested_amenities = Column(MutableDict.as_mutable(HSTORE))
    requested_accessibility = Column(MutableDict.as_mutable(HSTORE))
    requested_equipment = Column(MutableDict.as_mutable(HSTORE))
    requested_suitability = Column(MutableDict.as_mutable(HSTORE))
    requested_facilitators = Column(MutableDict.as_mutable(HSTORE))
    amenities = Column(MutableDict.as_mutable(HSTORE))
    accessibility = Column(MutableDict.as_mutable(HSTORE))
    equipment = Column(MutableDict.as_mutable(HSTORE))
    suitability = Column(MutableDict.as_mutable(HSTORE))
    facilitators = Column(MutableDict.as_mutable(HSTORE))
    comment = Column(String)

    def __init__(self, person, organisation, text, facilitation, resource, amenities=None, accessibility=None, equipment=None, suitability=None, facilitators=None):
        self.person = person
        self.organisation = organisation
        self.resource = resource
        self.requested_resource = resource
        self.text = text
        self.facilitation = facilitation
        self.requested_repeating_slots = []
        self.requested_single_slots = []
        self.repeating_slots = []
        self.single_slots = []
        self.strotime_slots = []
        self.status = "Pending"
        self.application_time = datetime.now()
        self.requested_amenities = amenities
        self.requested_accessibility = accessibility
        self.requested_equipment = equipment
        self.requested_suitability = suitability
        self.requested_facilitators = facilitators
        self.amenities = amenities
        self.accessibility = accessibility
        self.equipment = equipment
        self.suitability = suitability
        self.facilitators = facilitators

    def request_repeating_slot(self, repeating_slot):
        repeating_slot.application = self
        self.requested_repeating_slots.append(repeating_slot)

    def request_single_slot(self, slot):
        slot.application = self
        self.requested_single_slots.append(slot)

    def add_single_slot(self, slot):
        slot.application = self
        self.single_slots.append(slot)

    def add_repeating_slot(self, repeating_slot):
        repeating_slot.application = self
        self.repeating_slots.append(repeating_slot)

    def add_strotime_slot(self, strotime_slot):
        strotime_slot.application = self
        self.strotime_slots.append(strotime_slot)

    def __find_by_id(self, slots, slot_id):
        for slot in slots:
            if slot.id == slot_id:
                return slot
        return None

    def find_single_slot_by_id(self, slot_id):
        return self.__find_by_id(self.single_slots, slot_id)

    def find_repeating_slot_by_id(self, slot_id):
        return self.__find_by_id(self.repeating_slots, slot_id)

    def find_strotime_slot_by_id(self, slot_id):
        return self.__find_by_id(self.strotime_slots, slot_id)

    @property
    def requested_slots(self):
        typename = self.get_type()
        if typename == "single":
            return self.requested_single_slots
        if typename == "repeating":
            return self.requested_repeating_slots
        if typename == "strotime":
            return self.requested_strotime_slots
        return []

    @property
    def slots(self):
        if self.requested_single_slots:
            if self.single_slots:
                return self.single_slots
            return self.requested_single_slots

        if self.requested_repeating_slots:
            if self.repeating_slots:
                return self.repeating_slots
            return self.requested_repeating_slots

        if self.strotime_slots:
            return self.strotime_slots

        return []

    @property
    def type(self):
        return self.get_type()

    def get_type(self):
        if self.requested_single_slots or self.single_slots:
            return "single"
        elif self.requested_repeating_slots or self.repeating_slots:
            return "repeating"
        elif self.strotime_slots:
            return "strotime"


rammetid_status_enums = Enum("Processing", "Finished", name="rammetid_status_types")


class UmbrellaOrganisation(UriResource, Base):
    __tablename__ = 'umbrella_organisations'


class RammetidSlot(Base):
    __tablename__ = 'rammetid_slots'
    id = Column(Integer, primary_key=True)
    week_day = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    rammetid_id = Column(Integer, ForeignKey("rammetid.id"))
    rammetid = relationship("Rammetid", lazy=False)

    def __init__(self,
                 week_day,
                 start_date, end_date,
                 start_time, end_time):
        check_dates_are_closed_interval(start_date, end_date)
        check_start_time_before_end_time(start_time, end_time)
        check_iso_week_day(week_day)

        self.week_day = week_day
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time


class Rammetid(Base):
    __tablename__ = 'rammetid'
    id = Column(Integer, primary_key=True)
    umbrella_organisation_id = Column(Integer, ForeignKey("umbrella_organisations.id"))
    umbrella_organisation = relationship("UmbrellaOrganisation", lazy=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    resource = relationship("Resource", lazy=False,
                            foreign_keys="Rammetid.resource_id")
    status = Column(rammetid_status_enums)
    create_time = Column(DateTime, nullable=False, default=datetime.now())
    rammetid_slots = relationship("RammetidSlot", lazy=False, cascade="all, delete-orphan",
                                  passive_deletes=True)

    def __init__(self, umbrella_organisation, resource):
        self.umbrella_organisation = umbrella_organisation
        self.resource = resource
        self.rammetid_slots = []
        self.status = "Processing"
        self.create_time = datetime.now()

    def add_rammetid_slot(self, rammetid_slot):
        rammetid_slot.application = self
        self.rammetid_slots.append(rammetid_slot)


class FesakSak(Base):
    __tablename__ = 'fesak_sak'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    application = relationship("Application", lazy=False)
    saksnummer = Column(String, nullable=False)
    ws_header = Column(String, nullable=False)
    ws_sak = Column(String, nullable=False)

    def __init__(self, application, saksnummer, ws_header, ws_sak):
        self.application = application
        self.saksnummer = saksnummer
        self.ws_header = ws_header
        self.ws_sak = ws_sak


class FesakJournalpost(Base):
    __tablename__ = 'fesak_journalpost'
    id = Column(Integer, primary_key=True)
    fesak_sak_id = Column(Integer, ForeignKey("fesak_sak.id"), nullable=False)
    fesak_sak = relationship("FesakSak", lazy=False)
    ws_header = Column(String, nullable=False)
    ws_journalpost = Column(String, nullable=False)

    def __init__(self, fesak_sak, ws_header, ws_journalpost):
        self.fesak_sak = fesak_sak
        self.ws_header = ws_header
        self.ws_journalpost = ws_journalpost


settings_types_enums = Enum("bool", "date", "int", name="settings_types_enums")


class Settings(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)
    type = Column(settings_types_enums)
