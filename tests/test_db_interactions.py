import os
import shutil
import sqlite3
from datetime import datetime
from tempfile import mkdtemp
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models import Base, Riders, PhysicalLocations, Trackers
from db_interactions import create, get_or_create, get_and_delete, set_up_engine
from unittest.mock import patch

class TestSetUpDB(TestCase):

    def setUp(self):
        self.env_1 = patch.dict('os.environ', {'DB_TYPE': 'sqlite:///', 'DB_URI': '/tmp/test_db.db'})

    def test_set_up_engine(self):
        test_engine = create_engine('sqlite:////tmp/test_db.db')
        with self.env_1:
            engine = set_up_engine()
        self.assertEqual(engine.url, test_engine.url)





class TestManipulatingData(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_ = mkdtemp()
        cls.temp_db = os.path.join(cls.temp_, 'test_db.db')
        engine = create_engine('sqlite:///' + cls.temp_db, echo=True)
        Base.metadata.create_all(engine)
        cls.Session = sessionmaker(bind=engine)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_)

    def setUp(self):
        self.conn = sqlite3.connect(self.temp_db)
        self.cur = self.conn.cursor()
        self.tables = self.cur.execute('SELECT NAME FROM sqlite_master WHERE TYPE = "table";').fetchall()
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        # clear all data in DB
        for table in self.tables:
            self.cur.execute(f'DELETE FROM {table[0]}')
        self.conn.commit()

    def test_create(self):
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
        create(self.session, Riders, **data_to_add)
        data_in_riders = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results_riders = (1, 'Bobby', 'Hill', '123',
                            'solo', 'finished', 'male', 'paid', 123.1, 'hello@bob.com')
        data_in_tracker_locations = self.cur.execute('SELECT * FROM tracker_locations').fetchall()[0]
        expected_results_locations = (1, 'Riders')
        self.assertEqual(data_in_riders, expected_results_riders)
        self.assertEqual(data_in_tracker_locations, expected_results_locations)

    def test_get_or_create_creating(self):
        data_to_get = {
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
        test_get = get_or_create(self.session, Riders, **data_to_get)
        data_in_riders = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results_riders = (1, 'Bobby', 'Hill', '123',
                                   'solo', 'finished', 'male', 'paid', 123.1, 'hello@bob.com')
        data_in_tracker_locations = self.cur.execute('SELECT * FROM tracker_locations').fetchall()[0]
        expected_results_locations = (1, 'Riders')
        self.assertEqual(data_in_riders, expected_results_riders)
        self.assertEqual(data_in_tracker_locations, expected_results_locations)
        # todo tighten this up?
        self.assertEqual(1, test_get[0].id)
        self.assertTrue(test_get[1])

    def test_get_or_create_getting(self):
        test_data = {
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
        params = tuple(test_data.values())
        query = "INSERT INTO riders VALUES (?,?,?,?,?,?,?,?,?,?)"
        self.cur.execute(query, params)
        # due to relationship between tables, manually add data to tracker_locations too
        tracker_locations_test_data = {'id': 1, 'type': 'Riders'}
        self.cur.execute(
            'INSERT INTO tracker_locations VALUES (?,?)',
            tuple(tracker_locations_test_data.values()))
        self.conn.commit()
        test_get = get_or_create(self.session, Riders, **test_data)
        self.assertFalse(test_get[1])
        self.assertEqual(test_get[0][0].id, 1)

    def test_get_or_create_trackers(self):
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
        get_or_create(self.session, PhysicalLocations, **physical_location)
        get_or_create(self.session, Trackers, **tracker)
        data_in_trackers = self.cur.execute('SELECT * FROM TRACKERS;').fetchall()[0]
        expected_results = (123456, '123456', 'working', '2017-01-01 00:00:00.000000',
                            '2015-01-02 00:00:00.000000', '2019-01-02 00:00:00.000000', 'lost_dot', None, 1)
        self.assertEqual(data_in_trackers, expected_results)

    # todo make sure ondelete and onupdate restrictions are maintained!

    def test_get_or_create_tracker_no_location(self):

        tracker = {
            'tkr_number': 123456,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
        }
        get_or_create(self.session, Trackers, **tracker)
        data_in_db = self.cur.execute('SELECT * FROM TRACKERS;').fetchall()[0]
        expected_results = (123456, '123456', 'working', '2017-01-01 00:00:00.000000',
                            '2015-01-02 00:00:00.000000', '2019-01-02 00:00:00.000000', 'lost_dot', None, None)
        self.assertEqual(data_in_db, expected_results)

    # todo more tests re data is added to TrackerLocations when new rider, physical location or personal location added

    def test_create_wrong_category(self):
        data_to_add = {
            'id': 1,
            'category': 'nonsense'
        }
        with self.assertRaises(IntegrityError):
            create(self.session, Riders, **data_to_add)

    def test_get_and_delete(self):
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
            'third_party_name': None,
            'location_id': 1,
        }

        self.cur.execute('INSERT INTO physical_locations VALUES (?, ?)', tuple(physical_location.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker.values()))
        self.conn.commit()
        get_and_delete(self.session, Trackers, **{'tkr_number': 123456})
        self.assertEqual(self.cur.execute('SELECT * FROM trackers').fetchall(), [])

    def test_get_and_delete_doesnt_exist(self):
        self.assertFalse(get_and_delete(self.session, Trackers, **{'tkr_number': 123534}))

    def test_get_and_delete_multi_data(self):
        physical_location = {
            'id': 1,
            'name': 'cp1'
        }
        tracker_1 = {
            'tkr_number': 123456,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'third_party_name': None,
            'location_id': 1,
        }
        tracker_2 = {
            'tkr_number': 123457,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'third_party_name': None,
            'location_id': 1,
        }
        tracker_3 = {
            'tkr_number': 123458,
            'esn_number': '123456',
            'current_status': 'working',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'third_party_name': None,
            'location_id': 1,
        }
        self.cur.execute('INSERT INTO physical_locations VALUES (?, ?)', tuple(physical_location.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_1.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_2.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_3.values()))
        self.conn.commit()
        get_and_delete(self.session, Trackers, commit=False, **{'tkr_number': 123456})
        get_and_delete(self.session, Trackers, commit=False, **{'tkr_number': 123457})
        get_and_delete(self.session, Trackers, commit=False, **{'tkr_number': 123458})
        self.session.commit()
        self.assertEqual(self.cur.execute('SELECT * FROM trackers').fetchall(), [])

    def test_sqla_sanitises_data_on_input(self):
        # attempt to drop trackers table
        test_data = {
            'id': 1,
            'first_name': 'DROP TABLE  trackers'
        }
        get_or_create(self.session, Riders, **test_data)
        current_tables = self.cur.execute('SELECT NAME FROM sqlite_master WHERE TYPE = "table";').fetchall()
        self.assertTrue(self.tables == current_tables)
        self.assertEqual(get_or_create(self.session, Riders, **{'id': 1})[0][0].id, 1)

    def test_update(self):
        pass

