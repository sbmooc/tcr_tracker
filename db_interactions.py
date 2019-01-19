"""A set of helper functions to interact with the DB, using SQLA ORM"""
# todo tidy up and add typehinting

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os

engine = None


def set_up_engine():
    db_type = os.environ.get('DB_TYPE')
    db_uri = os.environ.get('DB_URI')
    if db_type is not None and db_uri is not None:
        engine_ = create_engine(db_type + db_uri)
    else:
        engine_ = None
    return engine_


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    global engine
    if not engine:
        engine = set_up_engine()
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create(session, model, commit=True, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    if commit:
        session.commit()
    return instance


def get_or_create(session, model, commit=True, **kwargs):
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        return instances, False
    else:
        instance = create(session, model, commit=commit, **kwargs)
        return instance, True


def get_and_delete(session, model, commit=True, **kwargs):
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        for instance in instances:
            session.delete(instance)
            if commit:
                session.commit()
        return instances, True
    else:
        return False
