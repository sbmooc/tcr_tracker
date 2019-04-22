from unittest import TestCase, mock
from unittest.mock import mock_open

from tracker.models import Riders
from tracker.webserver import app

class WebTests(TestCase):

    def setUp(self):
        self.test_client = app.test_client()


class TestValidator(WebTests):

    def test_validator(self):
        result = self.test_client.get('/hello')
        assert result.status_code == 200
        print(result)


@mock.patch('tracker.webserver.db.session_scope', mock_open())
class TestWebServer(WebTests):

    @mock.patch('tracker.webserver.db.create')
    @mock.patch('tracker.webserver.Riders')
    def test_post_rider(self, mock_riders, mock_create):

        rider_details = {
            "first_name": "Graham",
            "last_name": "Dodds",
            "email": "hello@email.com",
            "cap_number": '171',
            'category': 'male'
        }
        self.test_client.post('/riders', data=rider_details)
        mock_create.assert_called_with(mock.ANY, mock_riders, **rider_details)


class TestGetRiders(WebTests):

    def setUp(self):

        self.mock_rider_list = [
            Riders(
                id=1, first_name='Graham', last_name='Dodds', email='hello@dodds.com',
                cap_number='150', category='pair'
            ),
            Riders(
                id=2, first_name='James', last_name='Frost', email='hello@frost.com',
                cap_number='190', category='male'

            ),
            Riders(
                id=3, first_name='Sarah', last_name='Knight', email='hello@knight.com',
                cap_number='177', category='female'
            ),
            Riders(
                id=4, first_name='Rachel', last_name='Sking', email='hello@sking.com',
                cap_number='200', category='female'

            ),
            Riders(
                id=5, first_name='Emily', last_name='Skong', email='hello@skong.com',
                cap_number='400', category='female'

            )
        ]

    @mock.patch('tracker.webserver.db.get_riders')
    def test_get_riders_simple(self, mock_get_riders):
        mock_get_riders.return_value = (self.mock_rider_list, self.mock_rider_list[-1])
        # pass no parameters, to use defaults
        self.test_client.get('/riders')
        expected_result = [
            {
                'id': 1,
                'first_name': 'Graham',
                'last_name': 'Dodds',
                'email': 'hello@dodds.com',
                'cap_number': '150',
                'category': 'pair'
            },
            {
                'id': 2,
                'first_name': 'James',
                'last_name': 'Frost',
                'email': 'hello@frost.com',
                'cap_number': '190',
                'category': 'pair'
            },
            {
                'id': 3,
                'first_name': 'Sarah',
                'last_name': 'Knight',
                'email': 'hello@knight.com',
                'cap_number': '177',
                'category': 'pair'
            },
            {
                'id': 4,
                'first_name': 'Rachel',
                'last_name': 'Sking',
                'email': 'hello@sking.com',
                'cap_number': '200',
                'category': 'pair'
            },
            {
                'id': 5,
                'first_name': 'Emily',
                'last_name': 'Skong',
                'email': 'hello@skong.com',
                'cap_number': '400',
                'category': 'pair'
            }
        ]
