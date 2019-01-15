import sys

from sqlalchemy.orm import sessionmaker
# TODO These appear as unused imports but they're not
from models import Trackers, TrackerLocations, PhysicalLocations, PersonalLocations, Riders
from sqlalchemy import create_engine, Table
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
    # todo make this less broad
    except Exception as e:
        print(e)
        return False


def insert_row(session, table_name: str, **kwargs):
    table = getattr(sys.modules[__name__], table_name)
    data_to_add = table(**kwargs)
    session.add(data_to_add)
    return commit_to_db(session)


def delete_row(session, table_name: str, row_id: int):
    table = getattr(sys.modules[__name__], table_name)
    obj = session.query(Riders).filter(table.id == row_id).all()
    if obj:
        session.delete(obj)
        return commit_to_db(session)
    else:
        return False


def update_row(session, table_name: str, row_id: int, update_values: dict):
    table = getattr(sys.modules[__name__], table_name)
    obj = session.query(table).filter(table.id == row_id).first()
    for key, value in update_values.items():
        obj.key = value
    return commit_to_db(session)


