import enum
import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, DATETIME, \
    ForeignKey, Float, Enum, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, class_mapper, ColumnProperty

Base = declarative_base()


class DateTimeEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()
        return json.JSONEncoder.default(self, o)


class BaseMixin(object):
    # todo - add a comment here to work out why i do this!!
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


class Trackers(Base, BaseMixin):

    __tablename__ = 'trackers'
    id = Column('id', Integer, primary_key=True)
    esn_number = Column('esn_number', String)
    working_status = Column('current_status',
                            Enum(WorkingStatus))
    loan_status = Column('loan_status', Enum(LoanStatus))
    last_test_date = Column('last_test', DATETIME)
    purchase = Column('purchase', DATETIME)
    warranty_expiry = Column('warranty', DATETIME)
    owner = Column('owner', Enum(OwnerChoices))
    rider_id = Column('rider_id', ForeignKey('riders.id'))
    location_id = Column('location_id', ForeignKey('tracker_locations.id'))


class TrackerLocations(Base, BaseMixin):

    __tablename__ = 'tracker_riders'
    id = Column('id', Integer, primary_key=True)
    tracker = Column('tracker_id', ForeignKey('trackers.id'), nullable=False)
    rider = Column('rider_id', ForeignKey('riders.id'))
    location = Column('location_id', ForeignKey('tracker_locations.id'))
    deposit_amount = Column('deposit_amount', Float)
    deposit_status = Column('deposit_status', Enum(DepositStatus))


class Locations(Base, BaseMixin):
    __tablename__ = 'tracker_locations'
    id = Column('id', Integer, primary_key=True)
    location = Column(String, unique=True)
    trackers = relationship('Trackers')


class Riders(Base, BaseMixin):

    __tablename__ = 'riders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    email = Column('email', String)
    cap_number = Column('cap_number', String)
    trackers = relationship('Trackers')
    category = Column('category', Enum(RiderCategories))


class Audit(Base):

    __tablename__ = 'audit_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    table = Column('table_name', String)
    # table_id = Column('table_id', Integer)
    data = Column('data', JSON)
    delete_ = Column('delete', Boolean)
    # todo when user table is implemented, ensure it is recorded here
    # user
