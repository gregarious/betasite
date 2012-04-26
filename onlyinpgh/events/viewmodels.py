from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from onlyinpgh.common.utils import get_std_thumbnail


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

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        return {
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
            #'thumb': get_std_thumbnail(self.image, 'standard'),
        }
