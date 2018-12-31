import os
import shutil
import sqlite3
from tempfile import mkdtemp
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_interactions import add_data
from models import Base


class TestDBInteractions(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_ = mkdtemp()
        cls.temp_db = os.path.join(cls.temp_, 'test_db.db')
        engine = create_engine('sqlite:///'+cls.temp_db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        cls.session = Session()
        cls.cur = sqlite3.connect(cls.temp_db).cursor()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_)

    def test_add_data_Riders(self):

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

        add_ = add_data(self.session, 'Riders', **data_to_add)
        self.assertTrue(add_)
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()[0]
        expected_results = (1, 'Bobby', 'Hill', '123',
                            'solo', 'finished', 'male', 'paid', 123.1, 'hello@bob.com')
        self.assertEqual(data_in_db, expected_results)

    def test_add_data_Trackers(self):
        pass

    def test_add_data_TrackerLocations(self):
        # data is added to TrackerLocations when new rider, physical location or personal location added
        pass
    def test_add_data_Riders_wrong_category(self):

        data_to_add = {
            'id': 1,
            'category': 'nonsense'
        }
        add_ = add_data(self.session, 'Riders', **data_to_add)
        self.assertFalse(add_)
        data_in_db = self.cur.execute('SELECT * FROM RIDERS;').fetchall()
        expected_results = []
        self.assertEqual(data_in_db, expected_results)
