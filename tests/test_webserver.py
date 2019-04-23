from unittest import TestCase, mock
from unittest.mock import mock_open

from werkzeug.datastructures import ImmutableMultiDict

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
class TestRiderEndpoints(WebTests):

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

    @mock.patch('tracker.webserver.db.get_riders')
    def test_get_riders_simple(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = (['mock1', 'mock2'], Riders(id=100))
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders')
        # assert db.get_riders called with right params
        mock_get_riders.assert_called_with(mock.ANY, 1, 26)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, b'["mock1", "mock2"]')

    @mock.patch('tracker.webserver.db.get_riders')
    def test_get_riders_no_data(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = ([], None)
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders')
        self.assertEqual(result.status_code, 204)

    @mock.patch('tracker.webserver.db.get_riders')
    def test_get_riders_bad_request(self, mock_get_riders):
        # return a mock list and a last rider with a high id
        mock_get_riders.return_value = ([], Riders(id=40))
        # pass no parameters, to use defaults
        result = self.test_client.get('/riders', query_string={'start': 50})
        self.assertEqual(result.status_code, 416)

    @mock.patch('tracker.webserver.db.get')
    def test_get_individual(self, mock_get):
        mock_get.return_value = 'mock_rider'
        result = self.test_client.get('/riders/1')
        mock_get.assert_called_with(mock.ANY, Riders, **{'id': 1})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, b'"mock_rider"')

    @mock.patch('tracker.webserver.db.get')
    def test_get_individual_no_data(self, mock_get):
        mock_get.return_value = None
        result = self.test_client.get('/riders/1')
        mock_get.assert_called_with(mock.ANY, Riders, **{'id': 1})
        self.assertEqual(result.status_code, 204)

    @mock.patch('tracker.webserver.db.update')
    def test_patch_individual(self, mock_update):
        mock_update.return_value = 'mock_rider'
        result = self.test_client.patch('/riders/1', data={'cap_number': 100})
        mock_update.assert_called_with(mock.ANY, Riders, ImmutableMultiDict([('cap_number', '100')]), **{'id': 1})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, b'"mock_rider"')

    @mock.patch('tracker.webserver.db.update')
    def test_patch_individual_fail(self, mock_update):
        mock_update.return_value = False
        result = self.test_client.patch('/riders/1', data={'cap_number': 100})
        mock_update.assert_called_with(mock.ANY, Riders, ImmutableMultiDict([('cap_number', '100')]), **{'id': 1})
        self.assertEqual(result.status_code, 204)

    def test_add_tracker_to_rider(self):
        result = self.test_client.post('/riders/1/assignTracker', data={'trackerId': 142, 'depositPaid': 100})
        pass

    def test_remove_tracker_from_rider(self):
        result = self.test_client.post('/riders/1/removeTracker', data={'trackerId': 142, 'depositToBeReturned': 100})
        pass

