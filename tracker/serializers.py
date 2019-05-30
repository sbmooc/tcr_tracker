from marshmallow import fields, Schema, RAISE
from marshmallow_sqlalchemy import ModelSchema
from tracker.models import TrackerLocations, Trackers, Riders, Locations, RiderNotes, RiderEvents


class RiderNotesSerializer(ModelSchema):
    class Meta:
        model = RiderNotes
        fields = (
            'datetime',
            'notes'
        )


class RiderEventsSerializer(ModelSchema):
    class Meta:
        model = RiderEvents


class RiderSerializer(ModelSchema):
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    capNumber = fields.String(attribute='cap_number')
    notes = fields.Nested(RiderNotesSerializer, many=True)
    events = fields.Nested(RiderEventsSerializer, many=True)
    tracker_assigned = fields.Nested(Trackers, many=True)

    class Meta:
        model = Riders
        fields = (
            'id',
            'firstName',
            'lastName',
            'email',
            'category',
            'notes',
            'events',
            'trackers_assigned',
            'capNumber'

        )

# todo fix this!!!
class TrackerSchema(ModelSchema):
    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')
    lastTestDate = fields.Date(attribute='last_test_date')
    warrantyExpiry = fields.Date(attribute='warranty_expiry')
    loanStatus = fields.String(attribute='loan_status')
    purchaseDate = fields.Date(attribute='purchase_date')
    rider = fields.Nested(RiderSerializer)

    class Meta:
        model = Trackers
        fields = ('id', 'esnNumber', 'workingStatus', 'loanStatus', 'purchaseDate')


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


class RiderChangeTrackerState(ModelSchema):

    trackers = fields.Nested(Trackers)
    depositBalance = fields.Float(attribute='balance')

    class Meta:
        model = Riders
        fields = ('trackers', 'id', 'depositBalance')


rider_response = RiderSerializer()
riders_response = RiderSerializer(many=True)
# rider_post_request = RiderPostSchema(unknown=RAISE)
# rider_patch_request = RiderPatchSchema(unknown=RAISE)

tracker_post_request = TrackerPostSchema(unknown=RAISE)
tracker_response = TrackerSchema()
trackers_response = TrackerSchema(many=True)
tracker_patch_request = TrackerPatchSchema()
rider_change_tracker_state = RiderChangeTrackerState()






