from datetime import datetime
from unittest import TestCase, mock
from unittest.mock import mock_open

from tracker.models import Riders, Trackers
from tracker.webserver import app


class WebTests(TestCase):

    def setUp(self):
        self.test_client = app.test_client()
        self.mock_riders = [
            Riders(id=1, first_name='Bob', last_name='Green', cap_number='100', email='hello@email.com',
                   category='male', trackers=[]),
            Riders(id=2, first_name='Lyle', last_name='Taylor', cap_number='105', email='hello@email.com',
                   category='male', trackers=[]),
        ]
        self.mock_trackers = [
            Trackers(id=1, esn_number='123', working_status='working', loan_status='with_rider',
                     last_test_date=datetime(2018, 1, 1), purchase_date=datetime(2018, 1, 1),
                     warranty_expiry=datetime(2018, 1, 1), owner='lost_dot'),
            Trackers(id=2, esn_number='456', working_status='working', loan_status='with_rider',
                     last_test_date=datetime(2018, 1, 1), purchase_date=datetime(2018, 1, 1),
                     warranty_expiry=datetime(2018, 1, 1), owner='lost_dot'),
        ]

    @staticmethod
    def _bytes_to_string(result):
        return result.data.decode(result.charset)


@mock.patch('tracker.webserver.db.session_scope', mock_open())
class TestRiderEndpoints(WebTests):

    @mock.patch('tracker.webserver.db.create')
    @mock.patch('tracker.webserver.Riders')
    def test_post_rider(self, mock_riders, mock_create):
        rider_details = {
            "firstName": 'Bob',
            "lastName": "Green",
            "email": "hello@email.com",
            "capNumber": '171',
            'category': 'male',
        }
        self.test_client.post('/riders', json=rider_details)
        mock_create.assert_called_with(mock.ANY, mock_riders, **rider_details)

    # todo this should get caught in validation tests
    def test_post_rider_error(self):
        rider_details = {
            "nonsense": 'Bob',
            "lastName": "Green",
            "email": "hello@email.com",
            "capNumber": '171',
            'category': 'male',
        }
        response = self.test_client.post('/riders', json=rider_details)
        self.assertEqual(response.status_code, 400)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_riders_simple(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = (self.mock_riders, Riders(id=2))
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders')
        # assert db.get_riders called with right params
        mock_get_riders.assert_called_with(mock.ANY, 1, 26, Riders)
        self.assertEqual(result.status_code, 200)
        expected_result = [
            {
              "capNumber": "100",
              "firstName": "Bob",
              "lastName": "Green",
              "id": 1,
              "trackers": [],
              "category": "male",
              "email": "hello@email.com"
            },
            {
              "capNumber": "105",
              "firstName": "Lyle",
              "lastName": "Taylor",
              "id": 2,
              "trackers": [],
              "category": "male",
              "email": "hello@email.com"

            }
        ]
        self.assertEqual(result.json, expected_result)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_riders_no_data(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = ([], None)
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders')
        self.assertEqual(result.status_code, 204)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_riders_bad_request(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = ([], Riders(id=40))
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders', query_string={'start': 50})
        self.assertEqual(result.status_code, 416)

    @mock.patch('tracker.webserver.db.get')
    def test_get_rider(self, mock_get):
        mock_get.return_value = self.mock_riders[0]
        result = self.test_client.get('/riders/1')
        mock_get.assert_called_with(mock.ANY, Riders, **{'id': 1})
        self.assertEqual(result.status_code, 200)
        expected_result = {"capNumber": "100",
                          "firstName": "Bob",
                          "lastName": "Green",
                          "id": 1,
                          "trackers": [],
                          "category": "male",
                          "email": "hello@email.com"}
        self.assertEqual(result.json,
                         expected_result)

    @mock.patch('tracker.webserver.db.get')
    def test_get_rider_no_data(self, mock_get):
        mock_get.return_value = None
        result = self.test_client.get('/riders/1')
        mock_get.assert_called_with(mock.ANY, Riders, **{'id': 1})
        self.assertEqual(result.status_code, 204)

    #todo replace mocks here
    @mock.patch('tracker.webserver.db.update')
    def test_patch_rider(self, mock_update):
        mock_update.return_value = 'mock_rider'
        result = self.test_client.patch('/riders/1', json={'capNumber': '100'})
        mock_update.assert_called_with(mock.ANY, Riders, {'capNumber': '100'}, id=1)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, b'"mock_rider"')

    @mock.patch('tracker.webserver.db.update')
    def test_patch_rider_fail(self, mock_update):
        mock_update.return_value = False
        # todo this should use application/json-merge-patch
        result = self.test_client.patch('/riders/1', json={'capNumber': '100'})
        mock_update.assert_called_with(mock.ANY, Riders, {'capNumber': '100'}, id=1)
        self.assertEqual(result.status_code, 204)

    # todo mock out the validation in these tests and test separately

    @mock.patch('tracker.webserver.db.create')
    @mock.patch('tracker.webserver.Trackers')
    def test_post_tracker(self, mock_trackers, mock_create):
        mock_tracker = {
            'esnNumber': '1234',
            'workingStatus': 'working',
            'lastTestDate': '2001-01-01',
            'warrantyExpiry': '2019-01-01'
        }
        self.test_client.post('/trackers', json=mock_tracker)
        mock_create.assert_called_with(mock.ANY, mock_trackers, **mock_tracker)

    @mock.patch('tracker.webserver.db.get')
    def test_get_tracker(self, mock_get):
        mock_get.return_value = self.mock_trackers[0]
        result = self.test_client.get('/trackers/1')
        mock_get.assert_called_with(mock.ANY, Trackers, **{'id': 1})
        self.assertEqual(result.status_code, 200)
        expected_result = {
            'esnNumber': '123',
            'id': 1,
            'loanStatus': 'with_rider',
            'purchaseDate': '2018-01-01',
            'workingStatus': 'working'
        }
        self.assertEqual(result.json,
                         expected_result)

    @mock.patch('tracker.webserver.db.get')
    def test_get_tracker_no_data(self, mock_get):
        mock_get.return_value = None
        result = self.test_client.get('/trackers/1')
        mock_get.assert_called_with(mock.ANY, Trackers, **{'id': 1})
        self.assertEqual(result.status_code, 204)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_trackers_simple(self, mock_get_resources):
        # return a mock list and a last rider with a high id
        mock_get_resources.return_value = (self.mock_trackers, Trackers(id=2))
        # pass no parameters, to use defaults
        result = self.test_client.get('/trackers')
        # assert db.get_riders called with right params
        mock_get_resources.assert_called_with(mock.ANY, 1, 26, Trackers)
        self.assertEqual(result.status_code, 200)
        expected_result = [
            {
                'id': 1,
                'esnNumber': '123',
                'workingStatus': 'working',
                'loanStatus': 'with_rider',
                'purchaseDate': '2018-01-01',
            },
            {
                'id': 2,
                'esnNumber': '456',
                'workingStatus': 'working',
                'loanStatus': 'with_rider',
                'purchaseDate': '2018-01-01',
            }
        ]
        self.assertEqual(result.json, expected_result)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_trackers_no_data(self, mock_get_resources):
        mock_get_resources.return_value = ([], None)
        # pass no parameters, to use defaults
        result = self.test_client.get('/trackers')
        self.assertEqual(result.status_code, 204)

    @mock.patch('tracker.webserver.db.get_resources')
    def test_get_trackers_bad_request(self, mock_get_resources):
        mock_get_resources.return_value = ([], Trackers(id=40))
        result = self.test_client.get('/trackers', query_string={'start': 50})
        self.assertEqual(result.status_code, 416)

    @mock.patch('tracker.webserver.db.update')
    def test_patch_tracker(self, mock_update):
        updated_tracker = self.mock_trackers[0]
        updated_tracker.esn_number = 100
        mock_update.return_value = updated_tracker
        result = self.test_client.patch('/trackers/1', json={'esnNumber': '100'})
        mock_update.assert_called_with(mock.ANY, Trackers, {'esnNumber': '100'}, id=1)
        self.assertEqual(result.status_code, 200)
        expected_result = {
            'id': 1,
            'esnNumber': '100',
            'workingStatus': 'working',
            'loanStatus': 'with_rider',
            'purchaseDate': '2018-01-01'
        }
        self.assertEqual(result.json, expected_result)

    @mock.patch('tracker.webserver.db.update')
    def test_patch_tracker_fail(self, mock_update):
        mock_update.return_value = False
        result = self.test_client.patch('/trackers/1', json={'esnNumber': '100'})
        mock_update.assert_called_with(mock.ANY, Trackers, {'esnNumber': '100'}, id=1)
        self.assertEqual(result.status_code, 204)

    # def test_add_tracker_to_rider(self):
    #     result = self.test_client.post('/riders/1/assignTracker', data={'trackerId': 142, 'depositPaid': 100})
    #     pass
    #
    # def test_remove_tracker_from_rider(self):
    #     result = self.test_client.post('/riders/1/removeTracker', data={'trackerId': 142, 'depositToBeReturned': 100})
    #     pass

