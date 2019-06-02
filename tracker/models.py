import enum

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
from sqlalchemy.orm import relationship

from tracker.db_interactions import Base


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


class Trackers(Base, ):

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
    rider_assigned = Column('rider_assigned', ForeignKey('rider_assignment.id'))
    rider_possess = Column('rider_possess', ForeignKey('rider_possession.id'))
    #location = relationship('tracker_locations')


class RiderAssignment(Base):
    __tablename__ = 'rider_assignment'
    id = Column('id', Integer, primary_key=True)
    rider = Column('rider', ForeignKey('riders.id'))
    tracker = relationship('Trackers', uselist=False)


class RiderPossession(Base):
    __tablename__ = 'rider_possession'
    id = Column('id', Integer, primary_key=True)
    rider = Column('rider', ForeignKey('riders.id'))
    tracker = relationship('Trackers', uselist=False)


class TrackerAssignment(Base):
    __tablename__ = 'tracker_assignment'
    id = Column('id', Integer, primary_key=True)
    tracker = Column('tracker', ForeignKey('trackers.id'))
    rider = relationship('Riders', uselist=False)


class TrackerPossession(Base):
    __tablename__ = 'tracker_possession'
    id = Column('id', Integer, primary_key=True)
    tracker = Column('tracker', ForeignKey('trackers.id'))
    rider = relationship('Riders', uselist=False)


class Riders(Base, ):

    __tablename__ = 'riders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    email = Column('email', String)
    cap_number = Column('cap_number', String)
    category = Column('category', Enum(RiderCategories, validate_strings=True))
    notes = relationship('RiderNotes')
    tracker_assigned = Column('tracker_assigned', ForeignKey('tracker_assignment.id'))
    tracker_possesed = Column('tracker_possesed', ForeignKey('tracker_possession.id'))
    events = relationship('RiderEvents')
    balance = Column('balance', Float, default=0)
    # todo link riders who are in pairs? or does the capnumber do that???
    # todo add checkpoints stuff!

class TrackerLocations(Base, ):

    __tablename__ = 'tracker_locations'
    id = Column('id', Integer, primary_key=True)
    tracker = Column('tracker_id', ForeignKey('trackers.id'), nullable=False)
    rider = Column('rider', ForeignKey('riders.id'))
    # location = Column('location', ForeignKey('locations.id'))


class Locations(Base, ):
    __tablename__ = 'locations'
    id = Column('id', Integer, primary_key=True)
    location = Column(String, unique=True)
    # trackers = relationship('Trackers')

class RiderNotes(Base, ):
    __tablename__ = 'rider_notes'
    id = Column('id', Integer, primary_key=True)
    rider = Column(Integer, ForeignKey('riders.id'))
    datetime = Column('datetime', DATETIME)
    notes = Column('notes', String)
    user = Column(Integer, ForeignKey('users.id'))
    event = Column(Integer, ForeignKey('rider_events.id'))


class TrackerNotes(Base, ):
    __tablename__ = 'tracker_notes'
    id = Column('id', Integer, primary_key=True)
    tracker = Column(Integer, ForeignKey('trackers.id'))
    datetime = Column('datetime', DATETIME)
    user = Column(Integer, ForeignKey('users.id'))
    event = Column(Integer, ForeignKey('tracker_events.id'))


class RiderEvents(Base, ):
    __tablename__ = 'rider_events'
    id = Column('id', Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column('datetime', DATETIME)
    event_type = Column('event_type', Enum(RiderEventCategories))
    notes = relationship('RiderNotes')
    balance_change = Column('balance_change', Float)
    rider = Column(Integer, ForeignKey('riders.id'))


class TrackerEvents(Base, ):
    __tablename__ = 'tracker_events'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column('datetime', DATETIME)
    event_type = Column('event_type', Enum(TrackerEventCategories))
    notes = relationship('TrackerNotes')
    tracker = Column(Integer, ForeignKey('trackers.id'))


class Users(Base, ):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)

