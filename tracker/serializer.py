from marshmallow import fields, Schema, RAISE
from marshmallow_sqlalchemy import ModelSchema
from .models import TrackerLocations, Trackers, Riders, Locations


class RiderSchema(ModelSchema):
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    capNumber = fields.String(attribute='cap_number')

    class Meta:
        model = Riders


# todo fix this!!!
class TrackerSchema(ModelSchema):
    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')
    lastTestDate = fields.Date(attribute='last_test_date')
    warrantyExpiry = fields.Date(attribute='warranty_expiry')
    loanStatus = fields.String(attribute='loan_status')
    purchaseDate = fields.Date(attribute='purchase_date')
    rider = fields.Nested(RiderSchema)

    class Meta:
        model = Trackers
        fields = ('id', 'esnNumber', 'workingStatus', 'loanStatus', 'purchaseDate')


class RiderResponseSchema(RiderSchema):
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

    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')
    lastTestDate = fields.Date(attribute='last_test')
    warrantyExpiry = fields.Date(attribute='warranty_expiry')

    class Meta:
        model = Trackers
        fields = ('esnNumber', 'workingStatus', 'lastTestDate', 'warrantyExpiry', 'owner')


class TrackerPatchSchema(ModelSchema):

    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')
    lastTestDate = fields.Date(attribute='last_test')
    warrantyExpiry = fields.Date(attribute='warranty_expiry')

    class Meta:
        model = Trackers
        fields = ('esnNumber', 'workingStatus', 'lastTestDate', 'warrantyExpiry', 'owner')


rider_response = RiderResponseSchema()
riders_response = RiderResponseSchema(many=True)
rider_post_request = RiderPostSchema(unknown=RAISE)
rider_patch_request = RiderPatchSchema(unknown=RAISE)

tracker_post_request = TrackerPostSchema(unknown=RAISE)
tracker_response = TrackerSchema()
trackers_response = TrackerSchema(many=True)
tracker_patch_request = TrackerPatchSchema()






