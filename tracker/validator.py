from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from .models import TrackerLocations, Trackers, Riders, Locations


class TrackerSchema(ModelSchema):
    class Meta:
        model = Trackers


class RiderResponseSchema(ModelSchema):
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    capNumber = fields.String(attribute='cap_number')
    tracker = fields.Nested(TrackerSchema, many=True)

    class Meta:
        model = Riders
        fields = ('id', 'firstName', 'lastName', 'capNumber', 'trackers', 'email', 'category')


class RiderPostSchema(ModelSchema):
    firstName = fields.String(attribute='first_name', required=True)
    lastName = fields.String(attribute='last_name', required=True)
    capNumber = fields.String(attribute='cap_number', required=True)

    class Meta:
        model = Riders
        fields = ('firstName', 'lastName', 'capNumber', 'trackers', 'email', 'category')
        strict = True

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
# validate_something = api.model(
#     'Resource', {
#         'name': fields.String
#     })

