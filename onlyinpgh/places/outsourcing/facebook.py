from onlyinpgh.places.models import Place, Location, Hours, Parking
from onlyinpgh.outsourcing.apitools.facebook import GraphAPIClient, FacebookAPIError
from onlyinpgh.tokens import FACEBOOK_ACCESS_TOKEN

import re
import datetime

from onlyinpgh.places import abbreviate_state

from django.db import transaction

default_client = GraphAPIClient(FACEBOOK_ACCESS_TOKEN)


class FBPage(object):
    def __init__(self, fbpage_data, valid=None, api_error=None):
        self.data = fbpage_data
        self.valid = bool((valid is True) or (valid is None and self.data))
        self.api_error = api_error
        self._client = None

    @classmethod
    def import_live(cls, fbpage_id, client=None):
        '''
        Pull info for the given page from the Graph API.

        Will throw IOError or FacebookAPIError on failure response.
        '''
        client = client or default_client
        try:
            data = client.graph_api_page_request(fbpage_id)
            inst = cls(data)
        except FacebookAPIError as e:
            inst = cls({}, valid=False, api_error=e)
        inst._client = client
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
        if state != '' and len(state) != 2:
            state = abbreviate_state(state) or ''

        return Location(address=fb_loc.get('street', '').strip(),
                        town=fb_loc.get('city', '').strip(),
                        state=state,
                        postcode=fb_loc.get('zip', '').strip(),
                        latitude=fb_loc.get('latitude'),
                        longitude=fb_loc.get('longitude'))

    def get_picture(self, size='normal', timeout=None):
        '''Will query live service, may return IO/FB exceptions'''
        fb_id = self.data.get('id')
        if fb_id is None:
            return None
        client = self._client or default_client
        return client.graph_api_picture_request(self.data['id'], size=size, timeout=timeout)

    def get_field(self, fbkey, default=None):
        '''returns the data contained in the FB data specified by the fbkey'''
        return self.data.get(fbkey, default)


@transaction.commit_on_success
def fbpage_to_place(fbpage, save=False):
    if not fbpage.valid:
        return None

    p = Place()

    # special parking/hours objects used to serialize to DB
    # TODO: this is temporary. dig into django custom model field to make less hacky
    hours = fbpage.get_hours()
    if hours:
        p.set_hours(hours)
    parking = fbpage.get_parking()
    if parking:
        p.set_parking(parking)

    location = fbpage.get_location()
    if location is not None and save:
        location.save()

    p.location = location
    p.name = fbpage.get_field('name', '').strip()[:200]
    p.fb_id = fbpage.get_field('id', '').strip()[:50]
    p.description = fbpage.get_field('description', '').strip()
    # if no description, try 'about'
    if not p.description:
        p.description = fbpage.get_field('about', '').strip()
    p.phone = fbpage.get_field('phone', '').strip()[:200]
    p.url = fbpage.get_field('website', '').strip()
    if p.url:
        p.url = p.url.split()[0][:200]

    try:
        # TODO: download image once media is figured out
        p.image_url = fbpage.get_picture()
    except IOError:
        # TODO: log network error
        pass

    if save:
        p.save()
    return p


def supplement_place_data(place, force_sync_fields=[], exclude_fields=[]):
    '''
    Given a Place with a FB id, fleshes out all the empty entries with
    those from Facebook. The given place will be saved as a result of
    this method.

    Any value in force_sync_fields will be overwritten by the value
    returned by the Graph API, regardless of value. Specify location
    fields to force sync by prefixing them: i.e. 'location.FIELDNAME'

    Any value in exclude_fields will NOT be updated by Facebook.

    Returns a list of fields that were written to. Note that fb_id
    won't be returned in this list, because it is overwritten with
    the current numerical id value on every call.

    Beware IOErrors and or non-migration FacebookAPIErrors.
    '''
    if not place.fb_id:
        raise AttributeError("This Place has no fb_id set!")

    try:
        fbpage = FBPage.import_live(place.fb_id)
    except FacebookAPIError as fb_error:
        # check for migration errors and fix them right now
        if fb_error.is_migration_error():
            new_fb_id = fb_error.get_migration_destination()
            print 'migration!', place.fb_id, 'to', new_fb_id
            if new_fb_id:
                place.fb_id = new_fb_id
                place.save()
            # try grabbing the page again
            fbpage = FBPage.import_live(place.fb_id)
        else:
            raise

    if not fbpage.valid:
        if fbpage.api_error:
            raise fbpage.api_error
        else:
            raise Exception('Unkown failure building FBPage object.')
    fbplace = fbpage_to_place(fbpage, save=False)

    fields_written = []
    attrs = ('name', 'description', 'phone', 'url', 'image_url', 'hours', 'parking')
    for attr_name in attrs:
        if attr_name not in exclude_fields:
            fb_attr = getattr(fbplace, attr_name)
            if attr_name in force_sync_fields or (fb_attr and not getattr(place, attr_name)):
                fields_written.append(attr_name)
                setattr(place, attr_name, fb_attr)

    # force the updating of the fb_id (to standardize fb ids to numbers)
    std_fb_id = fbpage.get_field('id')
    if std_fb_id:
        place.fb_id = std_fb_id

    # handle location specially
    if 'location' not in exclude_fields:
        fbloc = fbpage.get_location()
        if fbloc is not None:
            if place.location is None:
                # if no location set, the new FB location is it.
                # since FB location is unsaved, need to save before assigning
                fbloc.save()
                place.location = fbloc
                fields_written.append('location')
            else:
                # otherwise, new flesh out any missing entries in the current location with these
                attrs = ('address', 'town', 'postcode', 'state', 'country', 'latitude', 'longitude')
                for attr_name in attrs:
                    fb_attr = getattr(fbloc, attr_name)
                    attr_namespaced = 'location.' + attr_name
                    if attr_namespaced in force_sync_fields or (fb_attr and not getattr(place.location, attr_name)):
                        setattr(place.location, attr_name, fb_attr)
                        fields_written.append(attr_namespaced)
                place.location.save()

    place.save()
    return fields_written
