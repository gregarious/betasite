from onlyinpgh.places.models import Place, Location, Hours, Parking, PlaceMeta
from onlyinpgh.outsourcing.apitools.facebook import GraphAPIClient, SCENABLE_ACCESS_TOKEN

import re
import datetime

from onlyinpgh.places import US_STATE_MAP
state_name_to_abbrev = dict([(name, code) for code, name in US_STATE_MAP])

from django.db import transaction


class FBPage(object):
    def __init__(self, fbpage_data, valid=None, status_message='', dtretrieved=datetime.datetime.now()):
        self.data = fbpage_data
        if valid is None and self.data:
            self.valid = True
        else:
            self.valid = False
        self.status_message = status_message
        self.dtretrieved = dtretrieved

    @classmethod
    def import_live(cls, fbpage_id, client=None):
        '''
        Pull info for the given page from the Graph API
        '''
        if not client:
            client = GraphAPIClient(SCENABLE_ACCESS_TOKEN)
        data = client.graph_api_page_request(fbpage_id)
        # TODO: improve error handling and protect other methods if bad data is retrieved
        inst = cls(data)
        return inst

    def get_hours(self):
        '''returns a list of 2-tuples in day: hour-span format'''
        our_days = ('Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun')
        fb_days = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

        # first do a sanity check on the hours to ensure they're in the format we expect
        # will raise a ValueError is the format is off
        fb_hours = self.data.get('hours')
        if not fb_hours:
            return None

        if not hasattr(fb_hours, 'items'):
            raise ValueError('Unexpected format for "hours"')

        valid_days = '((' + ')|('.join(fb_days) + '))'
        key_pattern = re.compile(valid_days + '_\d+_((open)|(close))')
        val_pattern = re.compile('[0-2]\d:[0-5]\d')
        for k, v in fb_hours.items():
            if not isinstance(k, basestring) or not isinstance(v, basestring) or \
                not key_pattern.match(k) or not val_pattern.match(v):
                raise ValueError('Unexpected format for "hours"')

        # helper function to determine (assumes string is in '\d+(:\d+)' format)
        str_to_time = lambda s: datetime.time(*map(int, s.split(':'))).strftime('%I:%M%p').lower() if s else None

        # fill a dict with hour listings for all 7 days
        day_hours_map = {}
        for day, fbday in zip(our_days, fb_days):
            hour_list = []
            ctr = 1
            while True:
                prefix = "%s_%d_" % (fbday, ctr)
                open_time = str_to_time(fb_hours.get(prefix + 'open'))
                if not open_time:
                    break
                close_time = str_to_time(fb_hours.get(prefix + 'close'))
                hour_list.append('%s - %s' % (open_time, close_time))
                ctr += 1
            hours_str = ', '.join(hour_list) if len(hour_list) > 0 else 'Closed'
            day_hours_map[day] = hours_str

        # group into entries by consecutive days with identical hours
        d0 = our_days[0]
        entries = [[d0, d0, day_hours_map[d0]]]
        for day in our_days:
            hours = day_hours_map[day]
            if hours == entries[-1][2]:
                entries[-1][1] = day
            else:
                entries.append([day, day, hours])

        h = Hours()
        for start, end, hours in entries:
            if start == end:
                h.add_span(start, hours)
            else:
                h.add_span("%s-%s" % (start, end), hours)

        return h

    def get_parking(self):
        '''returns a places.models.Parking object'''

        # first do a sanity check on the hours to ensure they're in the format we expect
        # will raise a ValueError is the format is off
        fb_parking = self.data.get('parking')
        if fb_parking is None:
            return None
        if not hasattr(fb_parking, 'items'):
            raise ValueError('Unexpected format for "parking"')

        p = Parking()
        for k, v in fb_parking.items():
            if not isinstance(k, basestring) or len(k) == 0:
                raise ValueError('Unexpected format for "parking"')
            try:
                int(v)  # could use bool here, but don't want to OK any random string
            except TypeError, ValueError:
                raise ValueError('Unexpected format for "parking"')
            if bool(v):
                p.add_option(k)
        return p

    def get_location(self):
        '''returns a places.models.Location object'''
        fb_loc = self.data.get('location')
        if not fb_loc:
            return None
        state = fb_loc.get('state', '').strip()
        # State entry is often full state name
        if state != '' and state.upper() not in US_STATE_MAP:
            state = state_name_to_abbrev.get(state, '')

        return Location(address=fb_loc.get('street', '').strip(),
                        town=fb_loc.get('city', '').strip(),
                        state=state,
                        postcode=fb_loc.get('zip', '').strip(),
                        latitude=fb_loc.get('latitude'),
                        longitude=fb_loc.get('longitude'))

    def to_place(self):
        '''returns a new places.models.Place object'''
        p = Place()

        # special parking/hours objects used to serialize to DB
        # TODO: this is temporary. dig into django custom model field to make less hacky
        hours = self.get_hours()
        if hours:
            p.set_hours(hours)
        parking = self.get_parking()
        if parking:
            p.set_parking(parking)

        p.location = self.get_location()
        p.name = self.get_field('name', '').strip()
        p.fb_id = self.get_field('id', '').strip()
        p.description = self.get_field('description', '').strip()
        p.phone = self.get_field('phone', '').strip()
        p.url = self.get_field('website', '').strip()

        # TODO: download image once media is figured out
        p.image_url = self.get_field('picture').replace('_s.jpg', '_n.jpg').strip()
        return p

    def get_field(self, fbkey, default=None):
        '''returns the data contained in the FB data specified by the fbkey'''
        return self.data.get(fbkey, default)


@transaction.commit_on_success
def complete_place_data(place, save=True):
    '''
    Given a Place with a FB id, fleshes out all the empty entries with
    those from Facebook.
    '''
    if not place.fb_id:
        raise AttributeError("This Place has no fb_id set!")
    fbpage = FBPage.import_live(place.fb_id)
    fbplace = fbpage.to_place()

    attrs = ('name', 'description', 'phone', 'url', 'hours', 'parking')
    for attr_name in attrs:
        fb_attr = getattr(fbplace, attr_name)
        if fb_attr and not getattr(place, attr_name):
            setattr(place, attr_name, fb_attr)

    # force the updating of the fb_id (to standardize fb ids to numbers)
    std_fb_id = fbpage.get_field('fb_id')
    if std_fb_id:
        place.fb_id = std_fb_id

    # handle location specially
    fbloc = fbpage.get_location()
    if fbloc is not None:
        if place.location is None:
            # if no location set, the new FB location is it.
            # since FB location is unsaved, need to save before assigning
            if not save:
                raise NotImplementedError("Not yet supporintg save=False when setting new location.")
            else:
                fbloc.save()
            place.location = fbloc
        else:
            # otherwise, new flesh out any missing entries in the current location with these
            attrs = ('address', 'town', 'postcode', 'state', 'country', 'latitude', 'longitude')

            for attr_name in attrs:
                fb_attr = getattr(fbloc, attr_name)
                if fb_attr and not getattr(place.location, attr_name):
                    setattr(place.location, attr_name, fb_attr)
            place.location.save()

    # if we're using the facebook image, add a PlaceMeta entry to keep track of that
    if not place.image_url:
        place.image_url = fbplace.image_url
        if not save:
            raise NotImplementedError("Not yet supporintg save=False when setting fb_linked_image PlaceMeta.")
        else:
            PlaceMeta.objects.get_or_create(key='fb_linked_image', value=place.image_url, place=place)

    if save:
        place.save()
    return place
