import sys

from sqlalchemy.orm import sessionmaker
# TODO These appear as unused imports but they're not
from models import Trackers, TrackerLocations, \
    PhysicalLocations, PersonalLocations, Riders
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()
#
# add_rider = Riders(first_name='oli', last_name='coombs',
#                    cap_number='234', category='solo')
#
# session.add(add_rider)
# session.commit()

def build_session(drivername: str, username: str = None, password: str = None,
                  host: str = None, port: str = None, database: str = None,
                  query: str = None):
    db = URL(drivername, username=username, password=password,
          host=host, port=port, database=database, query=query)
    engine = create_engine(db)
    Session = sessionmaker(bind=engine)
    return Session()

def commit_to_db(session):
    try:
        session.commit()
        return True
    except:
        return False


def add_data(session, model_name: str, **kwargs):
    model = getattr(sys.modules[__name__], model_name)
    data_to_add = model(**kwargs)
    session.add(data_to_add)
    return commit_to_db(session)


def remove_data(session, model_name: str, id: int):
    model = getattr(sys.modules[__name__], model_name)
    data_to_remove = session.query(model).filter_by(id=id).all()



def update_rider_details():
    pass
