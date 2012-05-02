from onlyinpgh.outsourcing.apitools.facebook import GraphAPIClient, FacebookAPIError
from onlyinpgh.tokens import FACEBOOK_ACCESS_TOKEN

from onlyinpgh.places.models import Place, Location, PlaceMeta
from onlyinpgh.events.models import Event, EventMeta, Role
from onlyinpgh.places.outsourcing.facebook import FBPage, fbpage_to_place
from onlyinpgh.places import abbreviate_state
from onlyinpgh.outsourcing.places import resolve_location

from dateutil import parser as dtparser
from onlyinpgh.common.utils import imagefile_from_url
from django.utils.timezone import make_aware

from django.db import transaction
from django.db.models import Q

default_client = GraphAPIClient(FACEBOOK_ACCESS_TOKEN)


class FBEvent(object):
    def __init__(self, fbevent_data, valid=None, api_error=None):
        self.data = fbevent_data
        self.valid = bool((valid is True) or (valid is None and self.data))
        self.api_error = api_error
        self._client = None

    @classmethod
    def import_live(cls, fbevent_id, client=None):
        '''
        Pull info for the given page from the Graph API
        '''
        if not client:
            client = GraphAPIClient(FACEBOOK_ACCESS_TOKEN)
        try:
            data = client.graph_api_object_request(fbevent_id, metadata=True)
            if data.get('type') != 'event':
                raise Exception('Given ID "%s" is not a Facebook event!' % str(fbevent_id))
            data.pop('metadata')    # don't need it anymore
            inst = cls(data)
        except FacebookAPIError as e:
            inst = cls({}, valid=False, api_error=e)
        inst._client = client
        return inst

    def get_dtstart(self):
        dtstart_str = self.data.get('start_time')
        if not dtstart_str:
            return None
        # currently assuming all datetimes are in Eastern (time is relative to event location in fb data)
        return make_aware(dtparser.parse(dtstart_str), 'US/Eastern')

    def get_dtend(self):
        dtend_str = self.data.get('end_time')
        if not dtend_str:
            return None
        # currently assuming all datetimes are in Eastern (time is relative to event location in fb data)
        return make_aware(dtparser.parse(dtend_str), 'US/Eastern')

    def get_place(self, allow_import=True):
        '''
        Returns full Place object for this event's venue. If venue has an
        ID, full place info will be taken from a separate FB request.
        Otherwise, one will be cobbled together from the available info.

        If data has no 'venue' field, this will None. In this case, it
        might be worth calling get_field with the key 'location' to get
        a plaintext primitive place name as a fallback.

        If allow_import is True, the Place will be created from a FBPage
        imported on the spot if there is an ID specified for the venue.
        Otherwise, the venue id will be ignored

        Remember the location assigned to the Place is not saved, so simply
        saving the Place (or even saving the Location then the Place) won't
        work. Need to do this:
            place.location.save()
            place.location = place.location  # reassign so ModelField assignment statement handles the new ID
            place.save()
        '''
        place = None
        # if we've got a place ID to work with, pull the full Place
        fb_pid = self.get_venue_id()
        if fb_pid and allow_import:
            client = self._client or None
            try:
                fb_page = FBPage.import_live(fb_pid, client=client)
                if fb_page.valid:
                    place = fbpage_to_place(fb_page, save=False)
                    if place:
                        return place
            except IOError:     # if there's a network problem log it and move on
                # TODO: log network error
                pass

        # if venue isn't available, we're done
        venue = self.data.get('venue')
        if not venue:
            return None

        # couldn't get a linked place on Facebook
        place = Place(name=self.data.get('location', ''))

        if venue:
            state = venue.get('state', '').strip()
            # State entry is often full state name
            if state != '' and len(state) != 2:
                state = abbreviate_state(state) or ''

            place.location = Location(
                address=venue.get('street', '').strip(),
                town=venue.get('city', '').strip(),
                state=state,
                postcode=venue.get('zip', '').strip(),
                latitude=venue.get('latitude'),
                longitude=venue.get('longitude'))
        return place

    def get_venue_id(self):
        '''
        Return venue ID if one exists. None otherwise.
        '''
        return self.data.get('venue', {}).get('id')

    def get_picture_url(self, size='normal', timeout=None):
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
def fbevent_to_event(fbevent, allow_place_import=True, save=False):
    e = Event()
    e.name = fbevent.get_field('name', '').strip()
    e.description = fbevent.get_field('description', '').strip()
    e.dtstart = fbevent.get_dtstart()
    e.dtend = fbevent.get_dtend()
    e.url = fbevent.get_field('website', '').strip()   # fairly sure this isn't part of a Graph API Event

    place_fbpage_id = fbevent.get_venue_id()
    if place_fbpage_id:
        linked_places = Place.objects.filter(fb_id=place_fbpage_id)
        if len(linked_places) > 0:
            if len(linked_places) > 1:
                pass
                # TODO: need an admin warning generated about data cleanup
            e.place = linked_places[0]

    if not e.place:
        new_place = fbevent.get_place(allow_import=allow_place_import)
        if new_place:
            new_place.listed = False    # don't automatically list any place we're creating dynamically here

            if save:
                # see if inner Location needs saved
                if new_place.location_id is None and new_place.location is not None:
                    new_place.location.save()
                    # this statment is necessary for Django's stupid inner model handling
                    new_place.location = new_place.location
                new_place.save()
            e.place = new_place
        else:
            # worst case, we get a location string to use as a primitive
            e.place_primitive = fbevent.get_field('location', '')
    try:
        im_url = fbevent.get_picture_url(size='large')
        e.image = imagefile_from_url(im_url)
    except IOError:
        # TODO: log network error
        pass

    if save:
        e.save()
    return e


def find_stored_place(fb_event):
    venue_id = fb_event.get_venue_id()
    if venue_id is not None:
        linked_places = Place.objects.filter(fb_id=venue_id)
        if len(linked_places) > 0:
            if len(linked_places) > 1:
                # TODO: notify admin of some db maintenance needs
                pass
            return linked_places[0]


def resolve_place(new_place, candidate=None):
    '''
    Will attempt resolving a new place object with an existing one in the
    DB using various methods. Helper for add_fbevent.

    Returns None if no DB-linked place could be found
    '''
    print '  attempting place resolve for %s. candidate: %s' % (str(new_place), str(candidate))
    # 1: check if the place matches the candidate in name
    if candidate and candidate.name and candidate.name.lower() == new_place.name.lower():
        print '  using candidate! name match.'
        return candidate

    # all the rest of the attempts deal with the new place's location. if we don't have that, punt
    if not new_place.location:
        print '  resolve failed.'
        return None

    # resolve the location to normalize the address for the next steps
    resolved = resolve_location(new_place.location, retry=0)
    if resolved:
        new_place.location = resolved
    new_loc = new_place.location

    # 2: see if the new address matches the candidate address - use it if so.
    if candidate:
        if candidate.location and new_loc.address.lower() == candidate.location.address.lower():
            # do a sanity check on distances between candidate and new place
            if not new_loc.is_geocoded() or not candidate.location.is_geocoded() or \
                new_loc.distance_from(candidate.location) < .8:
                print '  using candidate! address match'
                return candidate
            else:
                print '  address matched, but geocoding failure'

    # 3: candidate is a bust, next go fishing for the place in the db at large with a location query
    # grab all locations in the area
    query = None
    qs = []
    if new_loc.is_geocoded():
        qs.append(Q(latitude__lt=(new_loc.latitude + 1e-3), latitude__gt=(new_loc.latitude - 1e-3),
                    longitude__lt=(new_loc.longitude + 1e-3), longitude__gt=(new_loc.longitude - 1e-3)))

    if new_loc.address:
        if new_loc.town and new_loc.state:
            qs.append(Q(address=new_loc.address, town=new_loc.town, state=new_loc.state))
        if new_loc.postcode:
            qs.append(Q(address=new_loc.address, postcode=new_loc.postcode))

    # construct composite q objects
    for q in qs:
        if query is None:
            query = q
        else:
            query |= q

    # if there are some potential locations, see if we can find a matching place
    candidate_locations = Location.objects.filter(query) if query else []
    if len(candidate_locations) > 0:
        candidates = Place.objects.filter(name=new_place.name, location__in=candidate_locations)
        if len(candidates) > 0:
            # TODO: rank based on distance
            print '  using db match!', candidates[0]
            return candidates[0]

    # all out of options: punt!
    print '  resolve failed.'
    return None


@transaction.commit_on_success
def add_fbevent(fb_event, place_candidate=None):
    '''
    Adds a single event from a FBEvent to the DB.

    place_candidate can be provided if there is a likely Place for this
    Event to take place at (e.g. the FB page-linked Place that listed the
    event). This place_candidate should be a DB-linked Place instance since
    it may be used as the new Event's place.
    '''
    fb_id = str(fb_event.get_field('id', ''))
    stored_place = find_stored_place(fb_event)
    if stored_place:
        # if there was an fb ID in the event's venue that links to one of our places, just manually set it
        event = fbevent_to_event(fb_event, allow_place_import=False, save=False)
        event.place = stored_place
        print '  using stored place'
        event.save()
    else:
        event = fbevent_to_event(fb_event, save=False)
        event.listed = False    # guilty until proven innocent (don't want to list events not DIRECTLY happening in a place we know about)
        if event.place:
            # if we're here, we've got a newly created Place associated with the event
            #  let's see if we can match it to any likely candidate existing places
            resolved = resolve_place(event.place, place_candidate)
            if not resolved:
                # this is a new place (genereted from fb_event location/venue data),
                #  need to deep-save it and mark it with an EventMeta
                if event.place.location:
                    event.place.location.save()
                    event.place.location = event.place.location
                event.place.listed = False
                event.place.save()
                event.place = event.place
                PlaceMeta.objects.get_or_create(place=event.place, key='dynamically_generated', value='fb_event:%s' % fb_id)
            else:
                event.place = resolved
                event.listed = True
        elif event.place_primitive and event.place_primitive.lower() == place_candidate.name.lower():
            # if the primitive name matches the place candidate's name, it's safe to use the candidate
            event.place = place_candidate
            event.listed = True
    event.save()
    if fb_id:
        EventMeta.objects.get_or_create(event=event, key='fb_synced_event', value=fb_id)
    return event


def add_place_events(place, owners=[], on_failure=None):
    '''
    Function to add all events connected to a place.
    '''
    print 'processing', place.name, '(fb id %s)' % place.fb_id
    stubs = default_client.graph_api_collection_request('%s/events' % str(place.fb_id))
    print 'found', len(stubs), 'events'
    for eid in [s.get('id') for s in stubs]:
        print 'processing event id', eid
        matching_events = EventMeta.objects.filter(key='fb_synced_event', value=unicode(eid))
        if len(matching_events) > 0:
            if len(matching_events) > 1:
                # TODO: notify admin about db problem
                pass
            event = matching_events[0]
            print eid, ' already exists'
        else:
            fb_event = FBEvent.import_live(eid)
            if not fb_event.valid:
                raise NotImplementedError('on_failure callback not yet implemented!')
            event = add_fbevent(fb_event, place)
            print eid, 'added'
            unverfied = '(unverfied)' if (PlaceMeta.objects.filter(place=event.place, key='dynamically_generated').count() > 0) else ''
            if event.place:
                print '  place: %s %s' % (event.place, unverfied)
            else:
                print '  place: %s (primitive) %s' % (event.place_primitive, unverfied)

        for owner in owners:
            Role.objects.get_or_create(event=event, role_type='owner', organization=owner)
