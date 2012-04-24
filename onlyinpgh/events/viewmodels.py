from django.contrib.auth.models import User


### MODEL-LIKE DATA COLLECTIONS ###
class EventData(object):
    def __init__(self, event, user=None):
        if isinstance(user, User):
            self.is_attending = event.attendee_set\
                                .filter(user=user, is_attending=True)\
                                .count() > 0
        else:
            self.is_attending = False
        field_attrs = [attr for attr in event.__dict__ if not attr.startswith('_')]
        for attr in field_attrs:
            setattr(self, attr, event.__dict__[attr])
