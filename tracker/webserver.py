#!/usr/bin/env python
from flask import jsonify, request, json
from flask_restplus import Resource, fields

from tracker import db_interactions as db
from tracker.models import Riders
from tracker.validator import api, validate_something, app


# @api.route('/hello', methods=['GET'])
# class HelloWorld(Resource):
#     @api.expect(validate_something, validate=True)
#     def get(self):
#         return jsonify({'hello': 'world'})


@api.route('/riders', methods=['POST', 'GET'])
class RidersRequests(Resource):

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

# riderModel = {
#     'firstName': fields.String(attribute='first_name'),
#     'lastName': fields.String(attribute='last_name'),
#     'email': fields.String,
#     'capNumber': fields.String(attribute='cap_number')
# }


@api.route('/riders/<int:id>', methods=['GET', 'PATCH'])
class IndividualRiderRequests(Resource):
    def __init__(self):
        super(IndividualRiderRequests, self).__init__()

    # @api.marshal_with(riderModel)
    def get(self, id):
        with db.session_scope() as session:
            data = db.get(session, Riders, **request.view_args)
            if data:
                return app.response_class(response=json.dumps(data),
                                          status=200,
                                          mimetype='application/json')
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


@api.route('/riders/<int:id>/assignTracker')
class IndividualRiderAddTracker(Resource):
    pass


@api.route('/riders/<int:id>/removeTracker')
class IndividualRiderRemoveTracker(Resource):
    pass

if __name__ == '__main__':
    app.run(debug=True)
