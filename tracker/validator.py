from flask import Flask
from flask_restplus import fields, Api


validate_something = api.model(
    'Resource', {
        'name': fields.String
    })

