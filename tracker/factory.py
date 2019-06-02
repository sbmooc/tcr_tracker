from datetime import datetime

import factory
from tracker.models import Trackers, Riders
from tests.test_utils import Session

class TrackerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Trackers
        sqlalchemy_session = Session

    id = factory.Sequence(lambda n: n+1)
    esn_number = factory.Sequence(lambda x: str(x+100000))
    working_status = 'working'
    owner = 'Lost Dot'
    loan_status = 'with_rider'
    warranty_expiry = datetime(2020, 1, 1)
    purchase_date = datetime(2018, 1, 1)
    last_test_date = datetime(2018, 6, 1)


class RiderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Riders
        sqlalchemy_session = Session

    id = factory.Sequence(lambda n: n+1)
    cap_number = factory.Sequence(lambda n: str(n+1))
    first_name = factory.Sequence(lambda x: str('Rider'+ str(x+1)))
    last_name = factory.Sequence(lambda x: str('Taylor'+ str(x+1)))
    email = 'email@email.com'
    balance = 100
    category = 'male'

