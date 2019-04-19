from unittest import TestCase, mock
from unittest.mock import mock_open

from tracker.webserver import app

class WebTests(TestCase):

    def setUp(self):
        self.test_client = app.test_client()


class TestValidator(WebTests):

    def test_validator(self):
        result = self.test_client.get('/hello')
        assert result.status_code == 200
        print(result)

@mock.patch('tracker.webserver.Riders')
@mock.patch('tracker.webserver.db.session_scope', mock_open())
@mock.patch('tracker.webserver.db.create')
class TestWebServer(WebTests):

    def test_post_rider(self, mock_create, mock_riders):

        rider_details = {
            "first_name": "Graham",
            "last_name": "Dodds",
            "email": "hello@email.com",
            "cap_number": '171',
            'category': 'male'
        }
        self.test_client.post('/riders', data=rider_details)
        mock_create.assert_called_with(mock.ANY, mock_riders, **rider_details)
