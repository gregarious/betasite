from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from onlyinpgh.common.utils import get_cached_thumbnail

import datetime


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
        self.pk = self.id

    def _add_dates(self, data):
        # TODO: really should test some of this logic
        # if it's happening in the same year as now, or within the next 45 days, use the start year
        if self.dtstart.year == now().year:
            use_startyear = False
        elif (self.dtstart - now()).days < 45:
            use_startyear = False
        else:
            use_startyear = True

        data['dtstart'] = self.dtstart.strftime('%b ') + \
                          self.dtstart.strftime('%d').lstrip('0') + \
                          (self.dtstart.strftime(' %Y') if use_startyear else '') + \
                          ', ' + self.dtstart.strftime('%I:%M%p').lstrip('0').lower()

        # if ends on sasme day, or on next day but on or before 2 am, don't use the day part of dtend
        if self.dtstart.day == self.dtend.day:
            use_endday = False
        elif (self.dtend - self.dtstart).days < 1 and self.dtend.time() <= datetime.time(2, 0):
            use_endday = False
        else:
            use_endday = True

        if use_endday:
            data['dtend'] = self.dtend.strftime('%b ') + \
                            self.dtend.strftime('%d ').lstrip('0') + \
                            self.dtend.strftime('%Y, ')
        else:
            data['dtend'] = ''
        data['dtend'] += self.dtend.strftime('%I:%M%p').lstrip('0').lower()

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        data = {
            'name': self.name,
            'description': self.description,
            'dtstart': str(self.dtstart),
            'dtend': str(self.dtend),
            'place': {
                'name': self.place.name,
                'location': {
                    'address': self.place.location.address,
                    'latitude': float(self.place.location.latitude) if self.place.location.latitude is not None else None,
                    'longitude': float(self.place.location.longitude) if self.place.location.longitude is not None else None,
                } if self.place.location else None,
            } if self.place else None,
            'place_primitive': self.place_primitive,
            'image': self.image.url if self.image else '',
            'tags': [{
                'name': tag.name,
                'permalink': reverse('tags-item-detail', kwargs={'tid': tag.id})
            } for tag in self.tags.all()],
            # special fields only for JSON output
            'permalink': reverse('event-detail', kwargs={'eid': self.id}),
            'thumb_small': get_cached_thumbnail(self.image, 'small').url if self.image else '',
            'thumb_standard': get_cached_thumbnail(self.image, 'standard').url if self.image else '',
        }
        self._add_dates(data)
        return data
