from django.contrib.auth.models import User
from onlyinpgh.common.core.viewmodels import ViewModel
from django.template import RequestContext, Context

DEFAULT_IMAGE_URL = 'http://www.lolmore.com/wp-content/gallery/cute-animals-awesome-overload/013q.jpg'


class EventFeedItem(ViewModel):
    '''
    Exposes the following data:
        event
            id
            name
            dtstart (datetime for Django, iso-formatted string for JSON)
            dtend   (datetime for Django, iso-formatted string for JSON)
            allday  (boolean)
            place
                id
                name
                location
                    address
            place_primitive (should only exist if place doesn't)
            image_url
            [tags]
                id
                name
        is_attending (True)
    '''
    def __init__(self, event, user=None):
        super(EventFeedItem, self).__init__()
        self.event = event
        if isinstance(user, User):
            self.is_attending = event.attendee_set\
                                    .filter(user=user, is_attending=True)\
                                    .count() > 0
        else:
            self.is_attending = False

    def to_data(self, *args, **kwargs):
        print 'to data on', unicode(self.event)
        data = super(EventFeedItem, self).to_data(*args, **kwargs)
        event_data = data.get('event')
        keepers = set(('id', 'name', 'dtstart', 'dtend', 'allday', 'place', 'image_url', 'tags', 'place_primitive'))
        for k in event_data.keys():
            if k not in keepers:
                event_data.pop(k)
        if not event_data['image_url']:
            event_data['image_url'] = DEFAULT_IMAGE_URL

        place_data = data['event'].get('place')
        keepers = set(('id', 'name', 'location'))
        if place_data:
            for k in place_data.keys():
                if k not in keepers:
                    place_data.pop(k)

        return data


class EventDetail(ViewModel):
    '''
        event
            id
            name
            dtcreated
            dtmodified
            dtstart (datetime for Django, iso-formatted string for JSON)
            dtend   (datetime for Django, iso-formatted string for JSON)
            allday  (boolean)
            place
                id
                name
                location
                    address
            place_primitive (should only exist if place doesn't)
            image_url
            tags
                id
                name
            invisible   (boolean)
        is_attending (True)
    '''
    def __init__(self, event, user=None):
        super(EventDetail, self).__init__()
        self.event = event
        if isinstance(user, User):
            self.is_attending = event.attendee_set\
                                    .filter(user=user, is_attending=True)\
                                    .count() > 0
        else:
            self.is_attending = False

    def to_data(self, *args, **kwargs):
        data = super(EventDetail, self).to_data(*args, **kwargs)
        place_data = data['event'].get('place')
        if place_data:
            for k in place_data.keys():
                if k not in ('id', 'name'):
                    place_data.pop(k)
        if not data['event']['image_url']:
            data['event']['image_url'] = DEFAULT_IMAGE_URL

        data['is_attending'] = self.event.attendee_set.\
                        filter(is_attending=True).count() > 0

        return data
