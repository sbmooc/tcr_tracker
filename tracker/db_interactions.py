"""A set of helper functions to interact with the DB, using SQLA ORM"""
# todo add typehinting

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


def set_up_engine():
    """
    Return a db engine to use, as long as env variables are set properly.

    :return:
    """
    db_type = 'sqlite:///'
    db_uri = ''
    if db_type is not None and db_uri is not None:
        engine_ = create_engine(db_type + db_uri)
    else:
        engine_ = None
    return engine_


@contextmanager
def session_scope(commit=False):
    """Provide a transactional scope around a series of operations."""
    engine = set_up_engine()
    Base.metadata.create_all(engine)
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


def create_(session, instance, commit=False):
    """
    Create a row in db.

    :param session: db session.
    :param model: db model to create row in.
    :param commit: bool as to whether commit immediately.
    :param kwargs: dictionary of data to store in db.
    :return: instance of model.
    """
    session.add(instance)
    if commit:
        try:
            session.commit()
            return instance
        except IntegrityError:
            return False
    else:
        return instance


def create(session, model, commit=False, **kwargs):
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
def get_resources(session, start, end, model):
    """
    Returns a list of resources from start id for limit and return the id of the last resource in the db
    :param session:
    :param start:
    :param end:
    :param model:
    :return:
    """
    last_resource = session.query(model).order_by(model.id.desc()).first()
    data = session.query(model).filter(model.id >= start, model.id < end).all()
    return data, last_resource


def get_or_create(session, model, commit=False, **kwargs):
    # todo docstring here
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        return instances, False
    else:
        instance = create(session, model, commit=commit, **kwargs)
        return instance, True


def get_and_delete(session, model, commit=False, **kwargs):
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


def update(session, model, to_be_updated: dict, commit=False, **filter_):
    # todo docstring here
    n_rows_updated = session.query(model).filter_by(**filter_).update(to_be_updated)
    if n_rows_updated > 0:
        if commit:
            session.commit()
        return get(session, model, **filter_)
    else:
        return False

