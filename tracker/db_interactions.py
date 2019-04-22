"""A set of helper functions to interact with the DB, using SQLA ORM"""
# todo add typehinting

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import os

# from tracker.models import Audit
from tracker.models import Riders


def set_up_engine():
    """
    Return a db engine to use, as long as env variables are set properly.

    :return:
    """
    db_type = os.environ.get('DB_TYPE')
    db_uri = os.environ.get('DB_URI')
    if db_type is not None and db_uri is not None:
        engine_ = create_engine(db_type + db_uri)
    else:
        engine_ = None
    return engine_


@contextmanager
def session_scope(commit=True):
    """Provide a transactional scope around a series of operations."""
    engine = set_up_engine()
    session = Session(bind=engine)
    if commit:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    else:
        yield session


def create(session, model, commit=True, **kwargs):
    """
    Create a row in db.

    :param session: db session.
    :param model: db model to create row in.
    :param commit: bool as to whether commit immediately.
    :param kwargs: dictionary of data to store in db.
    :return: instance of model.
    """
    instance = model(**kwargs)
    session.add(instance)
    if commit:
        try:
            session.commit()
            return instance
        except IntegrityError:
            return False


def get(session, model, **kwargs):
    # todo docstring here
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        return instances
    else:
        return False


# todo unit test this
def get_riders(session, start, end):
    """
    Returns a list of riders from start id for limit and return the id of the last rider in the db
    :param session:
    :param start:
    :param limit:
    :return:
    """
    last_rider = session.query(Riders).order_by(Riders.id.desc()).first()
    data = session.query(Riders).filter(Riders.id >= start, Riders.id < end).all()
    return data, last_rider


def get_or_create(session, model, commit=True, **kwargs):
    # todo docstring here
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        return instances, False
    else:
        instance = create(session, model, commit=commit, **kwargs)
        return instance, True


def get_and_delete(session, model, commit=True, **kwargs):
    # todo docstring here
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        for instance in instances:
            session.delete(instance)
            if commit:
                session.commit()
        return instances, True
    else:
        return False


# @audit
def update(session, model, update_, commit=True, **kwargs):
    # todo docstring here
    no_rows_updated = session.query(model).filter_by(**kwargs).update(update_)
    if no_rows_updated > 0:
        if commit:
            session.commit()
            return get(session, model, **kwargs)
    else:
        return False

# def audit(func):
#     def wrapper(*args, **kwargs):
#         data = args[1].as_dict()
#         name = args[1].__tablename__
#         audit_ = Audit(table=name,
#                        data=data)
#         args[0].add(audit_)
#         return func(*args, **kwargs)
#     return wrapper
#
#
