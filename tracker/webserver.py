#!/usr/bin/env python
from flask import jsonify, request, json, Flask, Request

from tracker import db_interactions as db
from tracker.models import Riders

app = Flask(__name__)

# riderResponseModel = api.model('Riders', {
#     'firstName': fields.String(attribute='first_name'),
#     'lastName': fields.String(attribute='last_name'),
#     'email': fields.String,
#     'capNumber': fields.String(attribute='cap_number'),
#     'id': fields.Integer,
#     'trackers': fields.List(fields.Integer),
#     'category': fields.String
# })
#
# riderPostRequest = api.model('Riders', {
#     'firstName': fields.String(attribute='first_name'),
#     'lastName': fields.String(attribute='last_name'),
#     'email': fields.String,
#     'category': fields.String,
#     'capNumber': fields.Integer
# })
#
# riderPostResponse = api.model('Riders', {
#     'firstName': fields.String(attribute='first_name'),
#     'lastName': fields.String(attribute='last_name'),
#     'email': fields.String,
#     'category': fields.String,
#     'id': fields.Integer
# })


@app.route('/riders', methods=['POST', 'GET'])
class RidersRequests(Request):

    def post(self):
        rider_details = request.form
        with db.session_scope() as session:
            data = db.create(session, Riders, **rider_details)
            return app.response_class(response=json.dumps(data),
                                      status=201,
                                      mimetype='application/json')

    def get(self):
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
                return app.response_class(response=json.dumps(data),
                                          status=200,
                                          mimetype='application/json')


@app.route('/riders/<int:id>', methods=['GET', 'PATCH'])
class IndividualRiderRequests(Request):

    def get(self, id):
        with db.session_scope() as session:
            data = db.get(session, Riders, **request.view_args)
            if data:
                return data
            else:
                return app.response_class(status=204)

    # todo use json-merge-patch application type here
    def patch(self, id):
        # todo sort slight differences in request naming dictionaries
        data_to_update = request.form
        with db.session_scope() as session:
            data = db.update(session, Riders, data_to_update, **request.view_args)
            if data:
                return app.response_class(response=json.dumps(data),
                                          status=200,
                                          mimetype='application/json')
            else:
                return app.response_class(status=204)


@app.route('/riders/<int:id>/assignTracker')
class IndividualRiderAddTracker(Resource):
    pass


@api.route('/riders/<int:id>/removeTracker')
class IndividualRiderRemoveTracker(Resource):
    pass

if __name__ == '__main__':
    app.run(debug=True)
