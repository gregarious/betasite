from django.contrib.auth.models import User


class SpecialData(object):
    def __init__(self, special, user=None):
        fields = ('id', 'title', 'description', 'points', 'place',
                  'dexpires', 'dstart', 'total_available', 'total_sold',
                  'tags', 'get_absolute_url')
        if isinstance(user, User):
            coupons = special.coupon_set.filter(user=user)
            if coupons.count() == 0:
                self.coupon = None
            else:
                self.coupon = coupons[0]
        else:
            self.coupon = None

        for attr in fields:
            setattr(self, attr, getattr(special, attr))
        self.pk = self.id
        self._add_dates()

    def _add_dates(self):
        if self.dstart:
            self.dstart_str = self.dstart.strftime('%b ') + \
                              self.dstart.strftime('%d').lstrip('0') + \
                              self.dstart.strftime(', %Y')
        else:
            self.dstart_str = ''

        if self.dexpires:
            self.dexpires_str = self.dexpires.strftime('%b ') + \
                                self.dexpires.strftime('%d').lstrip('0') + \
                                self.dexpires.strftime(', %Y')
        else:
            self.dexpires_str = ''

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        return {
            'title': self.title,
            'description': self.description,
            'dstart': str(self.dstart),
            'dexpires': str(self.dexpires),
            'dstart_str': self.dstart_str,
            'dexpires_str': self.dexpires_str,
            'points': self.points,
            'place': {
                'name': self.place.name,
                'location': {
                    'address': self.place.location.address,
                    'latitude': float(self.place.location.latitude) if self.place.location.latitude is not None else None,
                    'longitude': float(self.place.location.longitude) if self.place.location.longitude is not None else None,
                    'is_gecoded': self.place.location.latitude is not None and self.place.location.longitude is not None,
                } if self.place.location else None,
                'permalink': self.place.get_absolute_url(),
            } if self.place else None,
            'total_available': self.total_available,
            'total_sold': self.total_sold,
            'tags': [{
                'name': tag.name,
                'permalink': tag.get_absolute_url()
            } for tag in self.tags.all()],
            # special fields only for JSON output
            'permalink': self.get_absolute_url(),
        }
