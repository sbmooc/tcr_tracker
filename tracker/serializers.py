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


class RidersInTrackers(ModelSchema):
    firstName = fields.String(attribute='first_name')
    lastName = fields.String(attribute='last_name')
    capNumber = fields.String(attribute='cap_number')

    class Meta:
        model = Riders
        fields = (
            'id',
            'capNumber',
            'firstName',
            'lastName',
            'capNumber'
        )


class TrackerSchema(ModelSchema):
    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')
    lastTestDate = fields.Date(attribute='last_test_date')
    warrantyExpiry = fields.Date(attribute='warranty_expiry')
    loanStatus = fields.String(attribute='loan_status')
    purchaseDate = fields.Date(attribute='purchase_date')
    rider = fields.Nested(RidersInTrackers, default=None)

    class Meta:
        model = Trackers
        fields = ('id',
                  'esnNumber',
                  'workingStatus',
                  'loanStatus',
                  'lastTestDate',
                  'purchaseDate',
                  'rider',
                  'warrantyExpiry')


class TrackerInRiders(ModelSchema):

    esnNumber = fields.String(attribute='esn_number')
    workingStatus = fields.String(attribute='working_status')

    class Meta:
        model = Trackers
        fields = ('id',
                  'esnNumber',
                  'workingStatus'
                  )


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

    trackers_assigned = fields.Nested(TrackerInRiders, many=True)
    depositBalance = fields.Float(attribute='balance')

    class Meta:
        model = Riders
        fields = (
            'trackers_assigned',
            'id',
            'depositBalance',
        )


single_rider = RiderSerializer()
many_riders = RiderSerializer(many=True)
rider_change_tracker_state = RiderChangeTrackerState()

single_tracker = TrackerSchema()
many_trackers = TrackerSchema(many=True)






