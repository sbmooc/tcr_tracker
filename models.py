from sqlalchemy import Column, Integer, String, DATETIME, \
    ForeignKey, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class StatusChoices(enum.Enum):
    working = 1
    broken = 2
    unknown = 3


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
    solo = 1
    pair = 2


class RiderGenders(enum.Enum):
    male = 1
    female = 2


class Trackers(Base):

    __tablename__ = 'trackers'
    tkr_number = Column('tkr_number', Integer, primary_key=True)
    esn_number = Column('esn_number', String)
    current_status = Column('current_status',
                            Enum(StatusChoices))
    last_test_date = Column('last_test', DATETIME)
    purchase = Column('purchase', DATETIME)
    warranty_expiry = Column('warranty', DATETIME)
    owner = Column('owner', Enum(OwnerChoices))
    third_party_name = Column('third_party_name', String)
    location_id = Column('location_id', ForeignKey('tracker_locations.id',
                                                   ondelete='restrict', onupdate='restrict'))


class TrackerLocations(Base):
    __tablename__ = 'tracker_locations'
    id = Column('id', Integer, primary_key=True)
    types = Column(String)
    trackers = relationship('Trackers')
    __mapper_args__ = {
        'polymorphic_on': types
    }


class Riders(TrackerLocations):

    __tablename__ = 'riders'
    id = Column(Integer, ForeignKey('tracker_locations.id'), primary_key=True,
                autoincrement=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    cap_number = Column('cap_number', String)
    category = Column('category', Enum(RiderCategories))
    status = Column('status', Enum(RiderStatus))
    gender = Column('gender', Enum(RiderGenders))
    deposit_status = Column('deposit_status', Enum(DepositStatus))
    deposit_amount = Column('deposit_amount', Float)
    email = Column('email', String)

    __mapper_args__ = {
        'polymorphic_identity': 'Riders'
    }

# TODO split out specifics associated with this race into another table?
# something like -- raceid, rider_id, status, category, deposit_status, deposit_amount


class PhysicalLocations(TrackerLocations):

    __tablename__ = 'physical_locations'
    id = Column(Integer, ForeignKey('tracker_locations.id'), primary_key=True,
                autoincrement=True)
    name = Column('physical_location', String)

    __mapper_args__ = {
        'polymorphic_identity': 'physical_locations'
    }


class PersonalLocations(TrackerLocations):

    __tablename__ = 'personal_locations'
    id = Column(Integer, ForeignKey('tracker_locations.id'), primary_key=True,
                autoincrement=True)
    name = Column('personal_location', String)

    __mapper_args__ = {
        'polymorphic_identity': 'personal_locations'
    }
