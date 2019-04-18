from flask import Flask
from flask_restplus import fields, Api

app = Flask(__name__)
api = Api(app)

validate_something = api.model(
    'Resource', {
        'name': fields.String
    })

