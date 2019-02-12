"""A set of helper functions to interact with the DB, using SQLA ORM"""
# todo add typehinting

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os

from tracker.models import Audit


def set_up_engine():
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
    instance = model(**kwargs)
    session.add(instance)
    if commit:
        session.commit()
    return instance


def get(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).all()
    if instances:
        return instances
    else:
        return False


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


def audit(func):
    def wrapper(*args, **kwargs):
        data = args[1].as_dict()
        name = args[1].__tablename__
        audit_ = Audit(table=name,
                       data=data)
        args[0].add(audit_)
        return func(*args, **kwargs)
    return wrapper


# @audit
def update(session, model, update_, commit=True, **kwargs):
    instance = get(session, model, **kwargs)
    if instance:
        session.query(model).filter_by(**kwargs).update(update_)
        if commit:
            session.commit()
    else:
        return False
