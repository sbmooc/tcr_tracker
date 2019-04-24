from marshmallow import fields, Schema
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
    email = fields.Email(required=True)

    class Meta:
        model = Riders
        fields = ('firstName', 'lastName', 'capNumber', 'trackers', 'email', 'category')


class RiderPatchSchema(ModelSchema):
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    capNumber = fields.String(attribute='cap_number')
    email = fields.Email()

    class Meta:
        model = Riders
        fields = ('firstName', 'lastName', 'capNumber', 'trackers', 'email', 'category')


class RiderAssignTracker(Schema):
    trackerId = fields.String(attribute='tracker_id', required=True)
    depositPaid = fields.String(attribute='deposit_paid', required=True)

class TrackerPostSchema(ModelSchema):

    # esn_number = Column('esn_number', String)
    # working_status = Column('current_status',
    #                         Enum(WorkingStatus))
    # loan_status = Column('loan_status', Enum(LoanStatus))
    # last_test_date = Column('last_test', DATETIME)
    # purchase = Column('purchase', DATETIME)
    # warranty_expiry = Column('warranty', DATETIME)
    # owner = Column('owner', Enum(OwnerChoices))
    # rider_id = Column('rider_id', ForeignKey('riders.id'))
    # location_id = Column('location_id', ForeignKey('tracker_locations.id'))

    class Meta:
        model = Trackers


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

