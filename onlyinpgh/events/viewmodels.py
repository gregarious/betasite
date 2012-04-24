from django.contrib.auth.models import User


class EventData(object):
    def __init__(self, event, user=None):
        fields = ('id', 'name', 'description', 'dtstart', 'dtend', 'image',
                  'url', 'place', 'place_primitive', 'tags', 'listed')
        if isinstance(user, User):
            self.is_attending = event.attendee_set\
                                .filter(user=user, is_attending=True)\
                                .count() > 0
        else:
            self.is_attending = False
        for attr in fields:
            setattr(self, attr, getattr(event, attr))
