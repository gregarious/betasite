from django.template import Context

from django.contrib.auth.models import User


class EventContext(Context):
    '''
    Exposes the following data:
        event (Event model instance)
        is_attending (boolean)
    '''
    def __init__(self, event, user=None, **kwargs):
        if isinstance(user, User):
            is_attending = event.attendee_set\
                                .filter(user=user, is_attending=True)\
                                .count() > 0
        else:
            is_attending = False

        super(EventContext, self).__init__(dict(
                event=event,
                is_attending=is_attending),
            **kwargs)
