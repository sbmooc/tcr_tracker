import enum
import json
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DATETIME,
    ForeignKey,
    Float,
    Enum,
    DATE
)
from sqlalchemy.orm import relationship, class_mapper, ColumnProperty

from tracker.db_interactions import Base

class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()
        return json.JSONEncoder.default(self, o)


class BaseMixin(object):
    # todo this looks to be for serializing json and probably isn't needed.
    def as_dict(self):
        result = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if isinstance(prop, ColumnProperty):
                result[prop.key] = getattr(self, prop.key)
        return result


class WorkingStatus(enum.Enum):
    working = 1
    broken = 2
    to_be_tested = 3
    unknown = 4


class LoanStatus(enum.Enum):
    with_rider = 1
    not_loaned = 2
    other = 3


class OwnerChoices(enum.Enum):
    lost_dot = 1
    rider_owned = 2
    third_party = 3


class DepositStatus(enum.Enum):
    not_yet_paid = 1
    paid = 2
    to_be_refunded = 3
    deposit_kept = 4
    refunded = 5


class RiderStatus(enum.Enum):
    not_yet_started = 1
    active = 2
    finished = 3
    scratched = 4


class RiderCategories(enum.Enum):
    male = 1
    female = 2
    pair = 3


class RiderEventCategories(enum.Enum):
    payment_in = 1
    payment_out = 2
    start_race = 3
    finish_race = 4
    scratch = 5
    arrive_checkpoint = 6


class TrackerEventCategories(enum.Enum):
    tested_OK = 1
    tested_broken = 2
    add_tracker_assignment = 3
    remove_tracker_assignment = 4
    add_tracker_possession = 5
    remove_tracker_possession = 6


class Trackers(Base, BaseMixin):

    __tablename__ = 'trackers'
    id = Column('id', Integer, primary_key=True)
    esn_number = Column('esn_number', String)
    working_status = Column('current_status',
                            Enum(WorkingStatus,
                                 validate_strings=True))
    loan_status = Column('loan_status', Enum(LoanStatus))
    last_test_date = Column('last_test', DATE)
    purchase_date = Column('purchase', DATE)
    warranty_expiry = Column('warranty', DATE)
    owner = Column('owner', Enum(OwnerChoices))
    rider_assigned = Column('rider_assigned', ForeignKey('riders.id'))
    # rider_possess = Column('rider_possess', ForeignKey('riders.id'))
    # location = relationship('tracker_locations')
    # todo - how to show possession???


class TrackerLocations(Base, BaseMixin):

    __tablename__ = 'tracker_locations'
    id = Column('id', Integer, primary_key=True)
    tracker = Column('tracker_id', ForeignKey('trackers.id'), nullable=False)
    rider = Column('rider', ForeignKey('riders.id'))
    # location = Column('location', ForeignKey('locations.id'))


class Locations(Base, BaseMixin):
    __tablename__ = 'locations'
    id = Column('id', Integer, primary_key=True)
    location = Column(String, unique=True)
    # trackers = relationship('Trackers')


class Riders(Base, BaseMixin):

    __tablename__ = 'riders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    email = Column('email', String)
    cap_number = Column('cap_number', String)
    trackers_assigned = relationship('Trackers')
    # trackers_possession = relationship('Trackers', back_populates='rider_possess')
    category = Column('category', Enum(RiderCategories, validate_strings=True))
    notes = relationship('RiderNotes')
    events = relationship('RiderEvents')
    balance = Column('balance', Float, default=0)
    # todo link riders who are in pairs? or does the capnumber do that???
    # todo add checkpoints stuff!


class RiderNotes(Base, BaseMixin):
    __tablename__ = 'rider_notes'
    id = Column('id', Integer, primary_key=True)
    rider = Column(Integer, ForeignKey('riders.id'))
    datetime = Column('datetime', DATETIME)
    notes = Column('notes', String)
    user = Column(Integer, ForeignKey('users.id'))
    event = Column(Integer, ForeignKey('rider_events.id'))


class TrackerNotes(Base, BaseMixin):
    __tablename__ = 'tracker_notes'
    id = Column('id', Integer, primary_key=True)
    tracker = Column(Integer, ForeignKey('trackers.id'))
    datetime = Column('datetime', DATETIME)
    user = Column(Integer, ForeignKey('users.id'))
    event = Column(Integer, ForeignKey('tracker_events.id'))


class RiderEvents(Base, BaseMixin):
    __tablename__ = 'rider_events'
    id = Column('id', Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column('datetime', DATETIME)
    event_type = Column('event_type', Enum(RiderEventCategories))
    notes = relationship('RiderNotes')
    balance_change = Column('balance_change', Float)
    rider = Column(Integer, ForeignKey('riders.id'))


class TrackerEvents(Base, BaseMixin):
    __tablename__ = 'tracker_events'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column('datetime', DATETIME)
    event_type = Column('event_type', Enum(TrackerEventCategories))
    notes = relationship('TrackerNotes')
    tracker = Column(Integer, ForeignKey('trackers.id'))


class Users(Base, BaseMixin):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)

