from unittest import TestCase
from tracker.webserver import app


class TestValidator(TestCase):

    def setUp(self) -> None:
        self.test_client = app.test_client()

    def test_validator(self):
        result = self.test_client.get('/hello')
        assert result.status_code == 200
        print(result)
