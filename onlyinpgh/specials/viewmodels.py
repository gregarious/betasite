from django.contrib.auth.models import User

from django.core.urlresolvers import reverse


class SpecialData(object):
    def __init__(self, special, user=None):
        fields = ('id', 'title', 'description', 'points', 'place',
                  'dexpires', 'dstart', 'total_available', 'total_sold',
                  'tags')
        if isinstance(user, User):
            if len(special.coupon_set.filter(user=user, was_used=False)) > 0:
                self.has_coupon = True
            else:
                self.has_coupon = False
        else:
            self.has_coupon = False

        for attr in fields:
            setattr(self, attr, getattr(special, attr))
        self.pk = self.id

    def _add_dates(self, data):
        data['dstart'] = self.dstart.strftime('%b ') + \
                         self.dstart.strftime('%d').lstrip('0') + \
                         self.dstart.strftime(', %Y')
        data['dexpires'] = self.dexpires.strftime('%b ') + \
                           self.dexpires.strftime('%d').lstrip('0') + \
                           self.dexpires.strftime(', %Y')

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        data = {
            'title': self.title,
            'description': self.description,
            'points': self.points,
            'place': {
                'name': self.place.name,
                'location': {
                    'address': self.place.location.address,
                    'latitude': float(self.place.location.latitude) if self.place.location.latitude is not None else None,
                    'longitude': float(self.place.location.longitude) if self.place.location.longitude is not None else None,
                } if self.place.location else None,
            } if self.place else None,
            'total_available': self.total_available,
            'total_sold': self.total_sold,
            'tags': [{
                'name': tag.name,
                'permalink': reverse('tags-item-detail', kwargs={'tid': tag.id})
            } for tag in self.tags.all()],
            # special fields only for JSON output
            'permalink': reverse('special-detail', kwargs={'sid': self.id}),
        }
        self._add_dates(data)
        return data
