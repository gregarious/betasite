from onlyinpgh.common.core.viewmodels import ViewModel


class EventFeedItem(ViewModel):
    def __init__(self, event, user=None):
        super(EventFeedItem, self).__init__()
        self.event = event

    def to_data(self):
        data = super(EventFeedItem, self).to_data()
        event_data = data.get('event')
        keepers = set(('id', 'name', 'dtstart', 'dtend', 'allday', 'place', 'image_url', 'tags'))
        for k in event_data.keys():
            if k not in keepers:
                event_data.pop(k)

        place_data = data['event'].get('place')
        keepers = set(('id', 'name'))
        if place_data:
            for k in place_data.keys():
                if k not in keepers:
                    place_data.pop(k)

        return data


class EventDetail(ViewModel):
    def __init__(self, event, user=None):
        super(EventDetail, self).__init__()
        self.event = event

    def to_data(self):
        data = super(EventDetail, self).to_data()
        place_data = data['event'].get('place')
        if place_data:
            for k in place_data.keys():
                if k not in ('id', 'name'):
                    place_data.pop(k)
        return data
