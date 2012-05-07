from django.contrib.auth.models import User

from django.utils.timezone import now
from onlyinpgh.common.utils import get_cached_thumbnail

import datetime
from django.template.defaultfilters import truncatewords


class EventData(object):
    def __init__(self, event, user=None):
        fields = ('id', 'name', 'description', 'dtstart', 'dtend', 'image',
                  'url', 'place', 'place_primitive', 'tags', 'listed',
                  'get_absolute_url')
        if isinstance(user, User):
            self.is_attending = event.attendee_set.filter(user=user).count() > 0
        else:
            self.is_attending = False
        for attr in fields:
            setattr(self, attr, getattr(event, attr))
        self.pk = self.id
        self._add_dates()

    def _add_dates(self):
        # TODO: really should test some of this logic
        # if it's happening in the same year as now, or within the next 45 days, use the start year
        if self.dtstart.year == now().year:
            use_year = False
        elif (self.dtstart - now()).days < 45:
            use_year = False
        else:
            use_year = True

        self.dtstart_str = self.dtstart.strftime('%b ') + \
                          self.dtstart.strftime('%d').lstrip('0') + \
                          (self.dtstart.strftime(' %Y') if use_year else '') + \
                          ', ' + self.dtstart.strftime('%I').lstrip('0') + \
                          (self.dtstart.strftime(':%M') if self.dtstart.minute != 0 else '') + \
                          self.dtstart.strftime('%p').lower()

        # if ends on sasme day, or on next day but on or before 2 am, don't use the day part of dtend
        if self.dtstart.day == self.dtend.day:
            if self.id == 13:
                print 'trigger 1'
            use_endday = False
        elif (self.dtend - self.dtstart).days < 1 and self.dtend.time() <= datetime.time(2, 0):
            if self.id == 13:
                print 'trigger 2'
            use_endday = False
        else:
            if self.id == 13:
                print 'trigger 3'
            use_endday = True

        if use_endday:
            self.dtend_str = self.dtend.strftime('%b ') + \
                            self.dtend.strftime('%d').lstrip('0') + \
                            (self.dtend.strftime(', %Y') if use_year else '') + ', '
        else:
            self.dtend_str = ''

        self.dtend_str += self.dtend.strftime('%I').lstrip('0') + \
                          (self.dtend.strftime(':%M') if self.dtend.minute != 0 else '') + \
                          self.dtend.strftime('%p').lower()

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        return {
            'id': self.id,
            'name': truncatewords(self.name, 4),
            'description': truncatewords(self.description, 10),
            'dtstart': str(self.dtstart),
            'dtend': str(self.dtend),
            'dtstart_str': self.dtstart_str,
            'dtend_str': self.dtend_str,
            'place': {
                'name': truncatewords(self.place.name, 4),
                'location': {
                    'address': self.place.location.address,
                    'latitude': float(self.place.location.latitude) if self.place.location.latitude is not None else None,
                    'longitude': float(self.place.location.longitude) if self.place.location.longitude is not None else None,
                    'is_gecoded': self.place.location.latitude is not None and self.place.location.longitude is not None,
                } if self.place.location else None,
                'permalink': self.place.get_absolute_url(),
            } if self.place else None,
            'place_primitive': truncatewords(self.place_primitive, 4),
            'image': self.image.url if self.image else '',
            'tags': [{
                'name': tag.name,
                'permalink': tag.get_absolute_url(),
            } for tag in self.tags.all()],
            # special fields only for JSON output
            'permalink': self.get_absolute_url(),
            'thumb_small': get_cached_thumbnail(self.image, 'small').url if self.image else '',
            'thumb_standard': get_cached_thumbnail(self.image, 'standard').url if self.image else '',
        }
