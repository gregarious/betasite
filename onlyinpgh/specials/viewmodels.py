from onlyinpgh.common.core.viewmodels import ViewModel


class SpecialFeedItem(ViewModel):
    def __init__(self, special, user=None):
        super(SpecialFeedItem, self).__init__()
        self.special = special

    def to_data(self, *args, **kwargs):
        data = super(SpecialFeedItem, self).to_data(*args, **kwargs)
        special_data = data.get('special')
        keepers = set(('id', 'title', 'points', 'place'))
        for k in special_data.keys():
            if k not in keepers:
                special_data.pop(k)

        place_data = data['special'].get('place')
        keepers = set(('id', 'name'))
        if place_data:
            for k in place_data.keys():
                if k not in keepers:
                    place_data.pop(k)

        return data


class SpecialDetail(ViewModel):
    def __init__(self, special, user=None):
        super(SpecialDetail, self).__init__()
        self.special = special

    def to_data(self, *args, **kwargs):
        data = super(SpecialDetail, self).to_data(*args, **kwargs)
        place_data = data['special'].get('place')
        if place_data:
            for k in place_data.keys():
                if k not in ('id', 'name'):
                    place_data.pop(k)
        return data
