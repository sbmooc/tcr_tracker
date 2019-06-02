from unittest import TestCase

from tracker.factory import RiderFactory, TrackerFactory
import tracker.serializers as sl


class TestSerializers(TestCase):

    def setUp(self):

        self.rider = RiderFactory()
        self.tracker = TrackerFactory()
        self.tracker.rider = self.rider
        self.tracker2 = TrackerFactory(loan_status='not_loaned')
        self.tracker3 = TrackerFactory(loan_status='not_loaned')
        RiderFactory()
        RiderFactory()
        RiderFactory()

    def test_rider_change_tracker_state(self):

        expected_result = {
            'id': 1,
            'depositBalance': 100,
            'trackers_assigned': [
                {
                    'id': 1,
                    'esnNumber': '100000',
                    'workingStatus': 'working',
                },
            ]
        }

        data = sl.rider_change_tracker_state.dump(self.rider)
        self.assertDictEqual(expected_result, data)

    def test_single_tracker(self):
        expected_result = {
            'id': 2,
            'esnNumber': '100001',
            'workingStatus': 'working',
            'lastTestDate': '2018-06-01',
            'warrantyExpiry': '2020-01-01',
            'loanStatus': 'with_rider',
            'purchaseDate': '2018-01-01',
            'rider': {
                'id': 1,
                'firstName': 'Rider1',
                'lastName': 'Taylor1',
                'capNumber': '1'
            }
        }
        data = sl.single_tracker.dump(self.tracker)
        self.maxDiff = None
        self.assertDictEqual(expected_result, data)

    def test_multiple_trackers(self):
        expected_result = [
            {
                'id': 2,
                'esnNumber': '100001',
                'workingStatus': 'working',
                'lastTestDate': '2018-06-01',
                'warrantyExpiry': '2020-01-01',
                'loanStatus': 'with_rider',
                'purchaseDate': '2018-01-01',
                'rider': {
                    'id': 1,
                    'firstName': 'Rider1',
                    'lastName': 'Taylor1',
                    'capNumber': '1'
                }
            },
            {
                'id': 3,
                'esnNumber': '100002',
                'workingStatus': 'working',
                'lastTestDate': '2018-06-01',
                'warrantyExpiry': '2020-01-01',
                'loanStatus': 'not_loaned',
                'purchaseDate': '2018-01-01',
                'rider': None
            },
            {
                'id': 4,
                'esnNumber': '100003',
                'workingStatus': 'working',
                'lastTestDate': '2018-06-01',
                'warrantyExpiry': '2020-01-01',
                'loanStatus': 'not_loaned',
                'purchaseDate': '2018-01-01',
                'rider': None
            },
        ]
        data = sl.many_trackers.dump([self.tracker, self.tracker2, self.tracker3])
        self.maxDiff = None
        self.assertCountEqual(expected_result, data)

    def test_rider(self):
        pass

    def test_riders(self):
        pass

