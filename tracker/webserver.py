#!/usr/bin/env python
from flask import jsonify, request, json
from flask_restplus import Resource

from tracker import db_interactions as db
from tracker.models import Riders
from tracker.validator import api, validate_something, app


# @api.route('/hello', methods=['GET'])
# class HelloWorld(Resource):
#     @api.expect(validate_something, validate=True)
#     def get(self):
#         return jsonify({'hello': 'world'})


@api.route('/riders', methods=['POST'])
class RidersRoutes(Resource):

    def post(self):
        rider_details = request.form
        with db.session_scope() as session:
            data = db.create(session, Riders, **rider_details)
            return app.response_class(response=json.dumps(data),
                                      status=201,
                                      mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
