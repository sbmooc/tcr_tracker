#!/usr/bin/env python
from flask import request, json, Flask

from tracker import db_interactions as db
from tracker.models import Riders, Trackers
from tracker import serializer as sl

app = Flask(__name__)


@app.route('/riders', methods=['POST'])
def post_riders():
    post_data = request.get_json()
    with db.session_scope() as session:
        data = db.create(session, Riders, **post_data)
        return app.response_class(response=sl.rider_response.dumps(data).data,
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
            return app.response_class(response=sl.riders_response.dumps(data),
                                      status=200,
                                      mimetype='application/json')


@app.route('/riders/<int:id>', methods=['GET'])
def get_rider(id):
    with db.session_scope() as session:
        data = db.get(session, Riders, **request.view_args)
        if data:
            return app.response_class(response=sl.rider_response.dumps(data),
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

@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/trackerAssignment',
           methods=['POST'])
def tracker_assignment_post(rider_id, tracker_id):
    pass

@app.route('/riders/<int:rider_id>/trackers/<int:tracker_id>/trackerAssignment',
           methods=['DELETE'])
def tracker_assignment_delete(rider_id, tracker_id):
    pass

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
