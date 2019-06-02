#!/usr/bin/env python
from datetime import datetime

import connexion
from flask import request, json, Flask

from tracker import db_interactions as db
from tracker.models import Riders, Trackers, TrackerEvents, TrackerNotes, RiderEvents, RiderNotes
from tracker import serializers as sl

app = Flask(__name__)


@app.route('/riders', methods=['POST'])
def post_riders():
    post_data = request.get_json()
    with db.session_scope() as session:
        data = db.create(session, Riders, **post_data)
        return app.response_class(response=sl.single_rider.dumps(data).data,
                                  status=201,
                                  mimetype='application/json')


@app.route('/riders', methods=['GET'])
def get_riders():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    end = start + limit
    with db.session_scope() as session:
        data, last_rider = db.get_resources(session, start, end, Riders)
        # if data is empty
        if last_rider is None:
            # todo put messages in response codes
            return app.response_class(status=204)
        # if request starts later than the last rider id
        if start > last_rider.id:
            # todo ensure that id is stored as an integer?
            # return some sort of 4xx status
            return app.response_class(status=416)
        else:
            return app.response_class(response=sl.many_riders.dumps(data),
                                      status=200,
                                      mimetype='application/json')


@app.route('/riders/<int:id>', methods=['GET'])
def get_rider(id):
    with db.session_scope() as session:
        data = db.get(session, Riders, **request.view_args)
        if data:
            return app.response_class(response=sl.single_rider.dumps(data),
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)


# todo use json-merge-patch application type here
@app.route('/riders/<int:id>', methods=['PATCH'])
def patch_rider(id):
    data_to_update = request.get_json()
    with db.session_scope() as session:
        data = db.update(session, Riders, data_to_update, **request.view_args)
        if data:
            # todo use serialization here
            return app.response_class(response=json.dumps(data),
                                      status=200,
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)


@app.route('/trackers', methods=['POST'])
def post_trackers():
    post_data = request.get_json()
    with db.session_scope() as session:
        data = db.create(session, Trackers, **post_data)
        return app.response_class(response=sl.tracker_response.dumps(data).data,
                                  status=201,
                                  mimetype='application/json')


@app.route('/trackers', methods=['GET'])
def get_trackers():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    end = start + limit
    with db.session_scope() as session:
        data, last_tracker = db.get_resources(session, start, end, Trackers)
        # if data is empty
        if last_tracker is None:
            # todo put messages in response codes
            return app.response_class(status=204)
        # if request starts later than the last rider id
        if start > last_tracker.id:
            # todo ensure that id is stored as an integer?
            # return some sort of 4xx status
            return app.response_class(status=416)
        else:
            return app.response_class(response=sl.trackers_response.dumps(data),
                                      status=200,
                                      mimetype='application/json')


@app.route('/trackers/<int:id>', methods=['GET'])
def get_tracker(id):
    with db.session_scope() as session:
        data = db.get(session, Trackers, **request.view_args)
        if data:
            return app.response_class(response=sl.tracker_response.dumps(data),
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)


# todo use json-merge-patch application type here
@app.route('/trackers/<int:id>', methods=['PATCH'])
def patch_tracker(id):
    data_to_update = request.get_json()
    with db.session_scope() as session:
        data = db.update(session, Trackers, data_to_update, **request.view_args)
        if data:
            return app.response_class(response=sl.tracker_response.dumps(data),
                                      status=200,
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)


def _check_rider_tracker_status(session, rider_id, tracker_id):
    tracker = db.get(session, Trackers, **{id: tracker_id})
    rider = db.get(session, Riders, **{id: rider_id})
    if not tracker:
        return app.response_class(status=404, response='Tracker not found')
    elif not rider:
        return app.response_class(status=404, response='Rider not found')
    else:
        return tracker, rider


def _create_event(session, model, user_id, datetime, event_type, tracker_id, **kwargs):
    return db.create_(
        session,
        model(
            user_id=user_id,
            datetime=datetime,
            event_type=event_type,
            tracker=tracker_id
        ),
    )


def _create_notes(session, model, datetime, id_to_link_notes_to, user_id, notes, event_id):
    return db.create_(
        session,
        model(
            tracker=id_to_link_notes_to,
            datetime=datetime,
            user=user_id,
            event=event_id,
            notes=notes
        ),
    )


@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/addTrackerAssignment',
           methods=['POST'])
def tracker_assignment_add(rider_id, tracker_id):
    now = datetime.now()
    request_payload = request.get_json()
    with db.session_scope() as session:
        tracker, rider = _check_rider_tracker_status(session, rider_id, tracker_id)
        db.update(
            session,
            Trackers,
            {
                'rider_assigned': rider_id
            },
            **{
                'id': tracker_id,
            },
        )
        created_tracker_event = _create_event(
            session,
            TrackerEvents,
            None,
            now,
            'add_tracker_assignment',
            tracker_id
        )
        _create_notes(
            session,
            TrackerNotes,
            now,
            tracker_id,
            None,
            request_payload['notes'],
            created_tracker_event.id
        )
        session.flush()
        created_rider_event = _create_event(
            session,
            RiderEvents,
            None,
            now,
            'payment_out',
            rider_id,
            **{
                'balance_change': request_payload['depositAmount']
            }
        )
        session.flush()
        _create_notes(
            session,
            RiderNotes,
            now,
            rider_id,
            None,
            request_payload['notes'],
            created_rider_event.id
        )
        db.update(
            session,
            Riders,
            {
                'deposit_balance': rider.balance - request_payload['depositAmount']
            },
            **{
                'id': rider_id
            }
        )
        try:
            session.commit()
        except:
            # todo put in logging!!!
            print('There has been an exception here!')
            session.rollback()
            raise
        return app.response_class(
            status=200,
            response=sl.rider_change_tracker_state.dumps(rider)
        )

@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/removeTrackerAssignment',
           methods=['POST'])
def tracker_assignment_remove(rider_id, tracker_id):
    now = datetime.now()
    request_payload = request.get_json()
    with db.session_scope() as session:
        tracker, rider = _check_rider_tracker_status(session, rider_id, tracker_id)
        db.update(
            session,
            Trackers,
            {
                'rider_assigned': None
            },
            **{
                'id': tracker_id,
            },
        )
        created_tracker_event = _create_event(
            session,
            TrackerEvents,
            None,
            now,
            'remove_tracker_assignment',
            tracker_id
        )
        _create_notes(
            session,
            TrackerNotes,
            now,
            tracker_id,
            None,
            request_payload['notes'],
            created_tracker_event.id
        )
        session.flush()
        created_rider_event = _create_event(
            session,
            RiderEvents,
            None,
            now,
            'payment_in',
            rider_id,
            **{
                'balance_change': request_payload['depositAmount']
            }
        )
        session.flush()
        _create_notes(
            session,
            RiderNotes,
            now,
            rider_id,
            None,
            request_payload['notes'],
            created_rider_event.id
        )
        db.update(
            session,
            Riders,
            {
                'deposit_balance': rider.balance + request_payload['depositAmount']
            },
            **{
                'id': rider_id
            }
        )
        try:
            session.commit()
        except:
            # todo put in logging!!!
            print('There has been an exception here!')
            session.rollback()
            raise
        return app.response_class(
            status=200,
            response=sl.rider_change_tracker_state.dumps(rider)
        )
@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/trackerPossession',
           methods=['POST'])
def tracker_possession_post(rider_id, tracker_id):
    pass

@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/trackerPossession',
           methods=['DELETE'])
def tracker_possession_delete(rider_id, tracker_id):
    pass

if __name__ == '__main__':
    app.run(debug=True)
