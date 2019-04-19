import os
import shutil

import sqlalchemy
import sqlite3
from datetime import datetime
from tempfile import mkdtemp
from unittest import TestCase, mock

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from tracker.models import Base, Riders, Trackers
from tracker.db_interactions import create, get_or_create, get_and_delete, set_up_engine, session_scope, update, \
    get_riders
from unittest.mock import patch, Mock


class DBTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_ = mkdtemp()
        cls.temp_db = os.path.join(cls.temp_, 'test_db.db')
        engine = create_engine('sqlite:///' + cls.temp_db)
        Base.metadata.create_all(engine)
        cls.TestSession = sessionmaker(bind=engine)
        cls.os_env = patch.dict('os.environ', {'DB_TYPE': 'sqlite:///', 'DB_URI': cls.temp_db})
        cls.test_engine = create_engine('sqlite:///' + cls.temp_db)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_)

    def setUp(self):
        self.conn = sqlite3.connect(self.temp_db)
        self.cur = self.conn.cursor()
        # todo ensure that this is turned on for sqlite3, remove once db is postgres??
        #   https://stackoverflow.com/questions/37034264/sqlite3-on-delete-restrict-via-sqlalchemy-not-being-honored-but-works-fine-in
        # self.cur.execute('PRAGMA foreign_keys=ON')
        # self.conn.commit()
        self.tables = self.cur.execute('SELECT NAME FROM sqlite_master WHERE TYPE = "table";').fetchall()
        self.test_session = self.TestSession()

    def tearDown(self):
        self.test_session.close()
        # clear all data in DB
        for table in self.tables:
            self.cur.execute(f'DELETE FROM {table[0]}')
        self.conn.commit()


class TestSetUpDB(DBTests):

    def test_set_up_engine(self):
        with self.os_env:
            engine = set_up_engine()
        self.assertEqual(engine.url, self.test_engine.url)

    def test_engine_None_with_no_env_vars(self):
        self.assertIsNone(set_up_engine())

    @mock.patch('tracker.db_interactions.set_up_engine')
    def test_session_scope(self, mock_engine):
        mock_engine.return_value = self.test_engine
        with session_scope() as session:
            rider = Riders(**{'id': 1})
            session.add(rider)
        result = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0][0]
        self.assertEqual(result, 1)

    @mock.patch('tracker.db_interactions.set_up_engine')
    def test_session_scope_with_error(self, mock_engine):
        sqlalchemy.orm.Session.rollback = Mock()
        mock_engine.return_value = self.test_engine
        rider = Riders(**{'id': 1})
        with session_scope() as session:
            session.add(rider)
        rider_1 = Riders(**{'id': 1})
        with self.assertRaises(IntegrityError):
            with session_scope() as s:
                s.add(rider_1)
        #assert session was rolled back
        sqlalchemy.orm.Session.rollback.assert_called()


class TestCRUD(DBTests):

    def test_create(self):
        data_to_add = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        create(self.test_session, Riders, **data_to_add)
        data_in_riders = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results_riders = (1, 'Bobby', 'Hill', 'hello@bob.com', '100', 'male')
        self.assertEqual(data_in_riders, expected_results_riders)

    def test_get_or_create_creating(self):
        data_to_get = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        test_get = get_or_create(self.test_session, Riders, **data_to_get)
        data_in_riders = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results_riders = (1, 'Bobby', 'Hill', 'hello@bob.com', '100', 'male')
        self.assertEqual(data_in_riders, expected_results_riders)
        self.assertEqual(1, test_get[0].id)
        self.assertTrue(test_get[1])

    def test_get_or_create_getting(self):
        test_data = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        params = tuple(test_data.values())
        query = "INSERT INTO riders VALUES (?,?,?,?,?,?)"
        self.cur.execute(query, params)
        self.conn.commit()
        test_get = get_or_create(self.test_session, Riders, **test_data)
        self.assertFalse(test_get[1])
        self.assertEqual(test_get[0][0].id, 1)

    def test_get_list_Riders(self):

        test_rider_1 = {
            'id': 1,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        test_rider_2 = {
            'id': 9,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        test_rider_3 = {
            'id': 15,
            'first_name': 'Bobby',
            'last_name': 'Hill',
            'email': 'hello@bob.com',
            'cap_number': 100,
            'category': 'male'
        }
        self.cur.execute('INSERT INTO riders VALUES (?, ?, ?, ?, ?, ?)', tuple(test_rider_1.values()))
        self.cur.execute('INSERT INTO riders VALUES (?, ?, ?, ?, ?, ?)', tuple(test_rider_2.values()))
        self.cur.execute('INSERT INTO riders VALUES (?, ?, ?, ?, ?, ?)', tuple(test_rider_3.values()))
        self.conn.commit()
        result = get_riders(self.test_session, 1, 10)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0][0].id, 1)
        self.assertEqual(result[0][1].id, 9)
        self.assertEqual(result[1].id, 15)

    def test_create_wrong_category(self):
        data_to_add = {
            'id': 1,
            'category': 'nonsense'
        }
        with self.assertRaises(IntegrityError):
            create(self.test_session, Riders, **data_to_add)

    def test_get_and_delete(self):
        tracker = {
            'id': 123456,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }

        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker.values()))
        self.conn.commit()
        get_and_delete(self.test_session, Trackers, **{'id': 123456})
        self.assertEqual(self.cur.execute('SELECT * FROM trackers').fetchall(), [])

    def test_get_and_delete_doesnt_exist(self):
        self.assertFalse(get_and_delete(self.test_session, Trackers, **{'id': 123534}))

    def test_get_and_delete_multi_data(self):
        tracker_1 = {
            'id': 123456,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        tracker_2 = {
            'id': 123457,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        tracker_3 = {
            'id': 123458,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_1.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_2.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_3.values()))
        self.conn.commit()
        get_and_delete(self.test_session, Trackers, commit=False, **{'id': 123456})
        get_and_delete(self.test_session, Trackers, commit=False, **{'id': 123457})
        get_and_delete(self.test_session, Trackers, commit=False, **{'id': 123458})
        self.test_session.commit()
        self.assertEqual(self.cur.execute('SELECT * FROM trackers').fetchall(), [])

    def test_sqla_sanitises_data_on_input(self):
        # attempt to drop trackers table
        test_data = {
            'id': 1,
            'first_name': 'DROP TABLE trackers'
        }
        get_or_create(self.test_session, Riders, **test_data)
        current_tables = self.cur.execute('SELECT NAME FROM sqlite_master WHERE TYPE = "table";').fetchall()
        self.assertTrue(self.tables == current_tables)
        self.assertEqual(get_or_create(self.test_session, Riders, **{'id': 1})[0][0].first_name, 'DROP TABLE trackers')

    def test_update(self):
        tracker_1 = {
            'id': 123456,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_1.values()))
        self.conn.commit()
        filter_ = {'id': 123456}
        updates = {'owner': 'third_party'}
        update(self.test_session, Trackers, updates, **filter_)
        result = self.cur.execute('SELECT * FROM trackers').fetchall()
        self.assertEqual(result[0], (123456, '123456', 'working',  'not_loaned', '2017-01-01 00:00:00',
                                     '2015-01-02 00:00:00', '2019-01-02 00:00:00',
                                     'third_party', 1, 1))

    def test_no_update_on_no_data(self):
        # nothing in db
        filter_ = {'id': 123456}
        updates = {'owner': 'third_party',
                   'third_party_name': 'TAW'}
        self.assertFalse(update(self.test_session, Trackers, updates, **filter_))

    def test_multiple_update(self):
        tracker_1 = {
            'id': 123456,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        tracker_2 = {
            'id': 123457,
            'esn_number': '123456',
            'working_status': 'working',
            'loan_status': 'not_loaned',
            'last_test_date': datetime(2017, 1, 1),
            'purchase': datetime(2015, 1, 2),
            'warranty_expiry': datetime(2019, 1, 2),
            'owner': 'lost_dot',
            'rider_id': 1,
            'location_id': 1,
        }
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_1.values()))
        self.cur.execute('INSERT INTO trackers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tracker_2.values()))
        self.conn.commit()
        filter_ = {'loan_status': 'not_loaned'}
        updates = {'loan_status': 'with_rider'}
        update(self.test_session, Trackers, updates, **filter_)
        result = self.cur.execute('SELECT * FROM trackers').fetchall()
        self.assertEqual(result[0], (123456, '123456', 'working',  'with_rider', '2017-01-01 00:00:00',
                                     '2015-01-02 00:00:00', '2019-01-02 00:00:00',
                                     'lost_dot', 1, 1))
        self.assertEqual(result[1], (123457, '123456', 'working',  'with_rider', '2017-01-01 00:00:00',
                                     '2015-01-02 00:00:00', '2019-01-02 00:00:00',
                                     'lost_dot', 1, 1))


class TestCRUDUsingContextMgr(DBTests):

    def setUp(self):
        super(TestCRUDUsingContextMgr, self).setUp()
        os.environ['DB_TYPE'] = 'sqlite:///'
        os.environ['DB_URI'] = self.temp_db

    def tearDown(self):
        super(TestCRUDUsingContextMgr, self).tearDown()
        del os.environ['DB_TYPE']
        del os.environ['DB_URI']

    def test_insert_multiple_rows_one_commit(self):
        riders = [{'id': 1}, {'id': 2}, {'id': 3}]
        with session_scope(commit=False) as session:
            for rider in riders:
                get_or_create(session,  Riders, commit=False, **rider)
            session.commit()
        result = self.cur.execute('SELECT * FROM RIDERS').fetchall()
        self.assertTrue(tuple(r[0] for r in result) == y['id'] for y in riders)

    def test_insert_multiple_rows_multiple_commits(self):
        riders = [{'id': 1}, {'id': 2}, {'id': 3}]
        with session_scope() as session:
            for rider in riders:
                get_or_create(session,  Riders, commit=False, **rider)
        result = self.cur.execute('SELECT * FROM RIDERS').fetchall()
        self.assertTrue(tuple(r[0] for r in result) == y['id'] for y in riders)
