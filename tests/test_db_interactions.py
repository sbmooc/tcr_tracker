import os
import shutil
import sqlite3
from datetime import datetime
from tempfile import mkdtemp
from unittest import TestCase, skip

from sqlalchemy import create_engine

from db_interactions import insert_row, delete_row, update_row
from models import Base, Session, Riders


def setup():
    pass
def teardown():
    # session.remove()
    pass

# def test_something():
#     instances = session.query(model.SomeObj).all()
#     eq_(0, len(instances))
#     session.add(model.SomeObj())
#     session.flush()
#     # ...
class TestDBInteractions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_ = mkdtemp()
        cls.temp_db = os.path.join(cls.temp_, 'test_db.db')
        # Base.metadata.create_all(engine)

    @classmethod
    def tearDownClass(cls):
        # shutil.rmtree(cls.temp_)
        pass

    def setUp(self):
        setup()
        self.conn = sqlite3.connect('/tmp/test_brexit.db')
        self.cur = self.conn.cursor()
        self.tables = self.cur.execute('SELECT NAME FROM sqlite_master WHERE TYPE = "table";').fetchall()
        # connect to the database
        # self.connection = engine.connect()
        # begin a non-ORM transaction
        # self.trans = self.connection.begin()
        # bind an individual Session to the connection
        # self.session = Session(bind=self.connection)

        engine = create_engine('sqlite:////tmp/test_brexit.db')
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()
    def tearDown(self):
        self.session.remove()
        # for table in self.tables:
        #     self.cur.execute(f'DROP TABLE {table[0]}')
        # self.session.close()
        # self.trans.rollback()
        # self.connection.close()

    def test_insert_data_riders(self):
        data_to_add = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'cap_number': '123',
            'category': 'solo',
            'status': 'finished',
            'gender': 'male',
            'deposit_status': 'paid',
            'deposit_amount': 123.1,
            'email': 'hello@bob.com'
        }
        add_ = Riders(**data_to_add)
        self.session.add(add_)
        self.session.commit()
        # add_ = insert_row(self.session, 'Riders', **data_to_add)
        # self.assertTrue(add_)
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results = (1, 'Bobby', 'Hill', '123',
                            'solo', 'finished', 'male', 'paid', 123.1, 'hello@bob.com')
        self.assertEqual(data_in_db, expected_results)

    def test_insert_data_trackers(self):
        #add data in physical locations table due to foreignkey constraint.
        physical_location = {
            'id': 1,
            'name': 'cp1'
        }

        tracker = {
            'tkr_number': 123456,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'location_id': 1,
        }
        self.assertTrue(insert_row(self.session, 'PhysicalLocations', **physical_location))
        self.assertTrue(insert_row(self.session, 'Trackers', **tracker))
        data_in_db = self.cur.execute('SELECT * FROM TRACKERS;').fetchall()[0]
        expected_results = (123456, '123456', 'working', '2017-01-01 00:00:00.000000',
                            '2015-01-02 00:00:00.000000', '2019-01-02 00:00:00.000000', 'lost_dot', None, 1)
        self.assertEqual(data_in_db, expected_results)

    # todo make sure ondelete and onupdate restrictions are maintained!

    def test_insert_data_trackers_no_location(self):

        tracker = {
            'tkr_number': 123456,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
        }
        self.assertTrue(insert_row(self.session, 'Trackers', **tracker))
        data_in_db = self.cur.execute('SELECT * FROM TRACKERS;').fetchall()[0]
        expected_results = (123456, '123456', 'working', '2017-01-01 00:00:00.000000',
                            '2015-01-02 00:00:00.000000', '2019-01-02 00:00:00.000000', 'lost_dot', None, None)
        self.assertEqual(data_in_db, expected_results)

    # data is added to TrackerLocations when new rider, physical location or personal location added
    def test_insert_data_trackerLocations_riders(self):
        data_to_add = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'cap_number': '123',
            'category': 'solo',
            'status': 'finished',
            'gender': 'male',
            'deposit_status': 'paid',
            'deposit_amount': 123.1,
            'email': 'hello@bob.com'
        }
        add_ = insert_row(self.session, 'Riders', **data_to_add)
        self.assertTrue(add_)
        data_in_db = self.cur.execute('SELECT * FROM tracker_locations;').fetchall()[0]
        expected_results = (1, 'riders')
        self.assertEqual(data_in_db, expected_results)

    def test_insert_data_trackerLocations_physical(self):
        data_to_add = {
            'id': 1,
            'name': 'cp1',
        }
        add_ = insert_row(self.session, 'PhysicalLocations', **data_to_add)
        self.assertTrue(add_)
        data_in_db = self.cur.execute('SELECT * FROM tracker_locations;').fetchall()[0]
        expected_results = (1, 'physical_locations')
        self.assertEqual(data_in_db, expected_results)

    def test_add_data_trackerlocations_personal(self):
        data_to_add = {
            'id': 1,
            'name': 'rory',
        }
        add_ = insert_row(self.session, 'PersonalLocations', **data_to_add)
        self.assertTrue(add_)
        data_in_db = self.cur.execute('SELECT * FROM tracker_locations;').fetchall()[0]
        expected_results = (1, 'personal_locations')
        self.assertEqual(data_in_db, expected_results)

    def test_insert_data_riders_wrong_category(self):
        data_to_add = {
            'id': 1,
            'category': 'nonsense'
        }
        add_ = insert_row(self.session, 'Riders', **data_to_add)
        self.assertFalse(add_)
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()
        expected_results = []
        self.assertEqual(data_in_db, expected_results)

    def test_delete_data_riders(self):
        query = "INSERT INTO riders VALUES (?,?,?,?,?,?,?,?,?,?)"
        params = (181197, "bobby", "holmes", "123", "solo",
                  "active", "male", "paid", 123.23, "hello@bob.com")
        self.cur.execute(query, params)
        # # sqlite doesn't allow multiple connections to the same DB, so close this connection
        self.conn.commit()
        self.conn.close()
        ridertoDelete = Riders(id=1)
        rider = self.session.query(Riders).filter(Riders.id==1).first()
        self.session.delete(rider)
        self.session.commit()
        # reopen connection
        # self.conn = sqlite3.connect(self.temp_db)
        # self.cur = self.conn.cursor()
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()
        expected_results = []
        self.assertEqual(data_in_db, expected_results)

    @skip
    def test_delete_nonexistentdata(self):
        # no data in db
        delete_ = delete_row(self.session, 'PhysicalLocations', 1)
        self.assertFalse(delete_)

    def test_update_rider(self):
        query = "INSERT INTO riders VALUES (?,?,?,?,?,?,?,?,?,?)"
        params = (1, "bobby", "holmes", "123", "solo",
                  "active", "male", "paid", 123.23, "hello@bob.com")
        self.cur.execute(query, params)
        # sqlite doesn't allow multiple connections to the same DB, so close this connection
        self.conn.close()
        update_ = update_row(self.session,
                             'Riders',
                             1,
                             {'first_name': 'oli',
                              'last_name': 'coombs'})
        self.assertTrue(update_)
        self.conn = sqlite3.connect(self.temp_db)
        self.cur = self.conn.cursor()
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()
        expected_results = []
        self.assertEqual(data_in_db, expected_results)


