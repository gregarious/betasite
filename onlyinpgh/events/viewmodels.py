from onlyinpgh.common.core.viewmodels import ViewModel


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
            image_url
            [tags]
                id
                name
        is_attending (True)
    '''
    def __init__(self, event, user=None):
        super(EventFeedItem, self).__init__()
        self.event = event

    def to_data(self, *args, **kwargs):
        data = super(EventFeedItem, self).to_data(*args, **kwargs)
        event_data = data.get('event')
        keepers = set(('id', 'name', 'dtstart', 'dtend', 'allday', 'place', 'image_url', 'tags'))
        for k in event_data.keys():
            if k not in keepers:
                event_data.pop(k)

        place_data = data['event'].get('place')
        keepers = set(('id', 'name', 'location'))
        if place_data:
            for k in place_data.keys():
                if k not in keepers:
                    place_data.pop(k)

        data['is_attending'] = self.event.attendee_set.\
                                filter(is_attending=True).count() > 0

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

    def to_data(self, *args, **kwargs):
        data = super(EventDetail, self).to_data(*args, **kwargs)
        event_data = data['event'].get('place')
        if event_data:
            for k in event_data.keys():
                if k not in ('id', 'name'):
                    event_data.pop(k)
        data['is_attending'] = self.event.attendee_set.\
                        filter(is_attending=True).count() > 0

        return data
