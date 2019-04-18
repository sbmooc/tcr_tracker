#!/usr/bin/env python
from flask import jsonify
from flask_restplus import Resource
from .validator import api, validate_something, app


@api.route('/hello', methods=['GET'])
class HelloWorld(Resource):
    @api.expect(validate_something, validate=True)
    def get(self):
        return jsonify({'hello': 'world'})


if __name__ == '__main__':
    app.run(debug=True)
