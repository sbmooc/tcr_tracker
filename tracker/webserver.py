#!/usr/bin/env python
from flask import jsonify, request, json, Flask, Request
from marshmallow import ValidationError, RAISE

from tracker import db_interactions as db
from tracker.models import Riders

from .validator import RiderResponseSchema, RiderPostSchema, RiderPatchSchema

app = Flask(__name__)

rider_response = RiderResponseSchema()
riders_response = RiderResponseSchema(many=True)
rider_post_request = RiderPostSchema(unknown=RAISE)
rider_patch_request = RiderPatchSchema(unknown=RAISE)

tracker_post_request = TrackerPostSchema(unknown=RAISE)

@app.route('/riders', methods=['POST'])
def post_riders():
    post_data = request.get_json()
    try:
        rider_post_request.load(post_data, transient=True)
    except ValidationError:
        return app.response_class(status=400)
    with db.session_scope() as session:
        # todo change db_interactions to input with serialized models
        data = db.create(session, Riders, **post_data)
        return app.response_class(response=rider_response.dumps(data).data,
                                  status=201,
                                  mimetype='application/json')


@app.route('/riders', methods=['GET'])
def get_riders():
    start = request.args.get('start', 1, type=int)
    limit = request.args.get('end', 25, type=int)
    end = start + limit
    with db.session_scope() as session:
        data, last_rider = db.get_riders(session, start, end)
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
            return app.response_class(response=riders_response.dumps(data),
                                      status=200,
                                      mimetype='application/json')


@app.route('/riders/<int:id>', methods=['GET'])
def get_rider(id):
    with db.session_scope() as session:
        data_ = db.get(session, Riders, **request.view_args)
        if data_:
            return app.response_class(response=rider_response.dumps(data_),
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)


# todo use json-merge-patch application type here
@app.route('/riders/<int:id>', methods=['PATCH'])
def patch_rider(id):
    data_to_update = request.get_json()
    try:
        rider_patch_request.load(data_to_update, transient=True)
    except ValidationError:
        return app.response_class(status=400)
    with db.session_scope() as session:
        data = db.update(session, Riders, data_to_update, **request.view_args)
        if data:
            return app.response_class(response=json.dumps(data),
                                      status=200,
                                      mimetype='application/json')
        else:
            return app.response_class(status=204)

# @app.route('/trackers', methods=['POST'])
# def post_trackers():
#     post_data = request.get_json()
#     try:
#         rider_request.load(post_data, transient=True)
#     except ValidationError:
#         return app.response_class(status=400)
#     with db.session_scope() as session:
#         # todo change db_interactions to input with serialized models
#         data = db.create(session, Riders, **post_data)
#         return app.response_class(response=rider_response.dumps(data).data,
#                                   status=201,
#                                   mimetype='application/json')

# @app.route('/riders/<int:id>/assignTracker')
# def assign_tracker(id):
#     data_to_update = request.get_json()
#     with db.session_scope() as session:
#         data = db.update(session, Riders, )
#
# @api.route('/riders/<int:id>/removeTracker')
# class IndividualRiderRemoveTracker(Resource):
#     pass

if __name__ == '__main__':
    app.run(debug=True)
