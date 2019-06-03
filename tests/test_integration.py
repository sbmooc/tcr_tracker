# Use known sqlite db with correct data in it.
# Start webserver on known port
# Send requests and expect known responses returned
from unittest import TestCase
from tracker.db_interactions import session_scope, set_up_engine, Base
from tracker.models import Riders, Trackers
from tracker.webserver import app

class TestTrackerAssignment(TestCase):

    def setUp(self):
        self.test_client = app.test_client()
        engine = set_up_engine()
        Base.metadata.create_all(engine)

    def test_tracker_assigned_OK(self):
        # add tracker and rider to db
        with session_scope() as session:
            rider = Riders(
                id=1
            )
            tracker = Trackers(
                id=1
            )
            session.add(rider)
            session.add(tracker)
            session.commit()
        self.test_client.post('/riders/1/trackers/1/addTrackerAssignment')
