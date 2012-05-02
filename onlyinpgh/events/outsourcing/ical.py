from onlyinpgh.events.models import Event, Role, EventMeta, ICalendarFeed

from django.utils import timezone
from django.db import transaction

import icalendar
import urllib
import pytz
import datetime
import re


def process_time(component, default_tz_str=None):
    '''
    Attempts to return a timezone-aware version of the component's
    datetime, trying in this order:
    - If time string ends in Z, it's UTC
    - If TZID is specified in the component
    - If a default_tz_str is specified

    If these steps fail, a the defawult timeone in the settings will
    be used.
    '''
    dt = component.dt
    try:
        # if its UTC, we'll already have an aware timezone
        if dt.tzinfo:
            return dt
    except AttributeError:
        # TODO: once allday is supported, use it
        # if no timezone attribute, it must be a regular date object. give it a time of midnight
        dt = datetime.datetime.combine(dt, datetime.time())

    # otherwise, we need to find a timezone and localize to it
    tz_str = component.params.get('TZID', default_tz_str)
    if tz_str is None:
        # TODO: log unavailable timezone message
        return timezone.make_aware(dt, timezone.get_current_timezone())
    try:
        return timezone.make_aware(dt, pytz.timezone(tz_str))
    except pytz.exceptions.UnknownTimeZoneError:
        # TODO: log unknown timezone message
        return timezone.make_aware(dt, timezone.get_current_timezone())


class FeedImporter(object):
    def __init__(self, feed_inst):
        '''initialize from an ICalendarFeed instance'''
        self.feed_instance = feed_inst

    @classmethod
    @transaction.commit_on_success
    def from_url(cls, url, feed_owner=None, candidate_places=[]):
        '''initialize from a url and Organization instance'''

        f = urllib.urlopen(url)
        ical = icalendar.Calendar.from_string(f.read())
        f.close()
        cal_name = ical.get('X-WR-CALNAME', url)

        feed, created = ICalendarFeed.objects.get_or_create(url=url)

        if feed_owner:
            # if we need to set the owner, but found an existing feed whose owner is different, fail
            if not created and feed.owner is not None and feed.owner != feed_owner:
                raise Exception('Feed already exists under different owner. Cannot create new one.')
            if not feed.owner:
                feed.owner = feed_owner

        if feed.name != cal_name:
            feed.name = cal_name

        if candidate_places:
            for candidate in candidate_places:
                feed.candidate_places.add(candidate)

        feed.save()
        return cls(feed, feed_owner)

    def import_new(self, start_filter=None):
        '''
        Import any events in the feed not already tracked by a
        VEventRecord. If provided, will ignore any events taking place
        before start_filter.

        Function is a generator object that will yield a collection of
        EventImportNotice objects, one per entry considered (that begins
        after the start_filter). If the event was not created successfully,
        the VEventRecord in the returned notice will not be savable to the
        db.
        '''
        f = urllib.urlopen(self.feed_instance.url)
        ical = icalendar.Calendar.from_string(f.read())
        f.close()

        default_tz_str = ical.get('X-WR-TIMEZONE')

        for entry in ical.walk('vevent'):
            event = self.process_entry(entry, default_tz_str, start_filter)
            if event:
                print event.id, event

    @transaction.commit_on_success
    def process_entry(self, entry, default_tz_str=None, start_filter=None):
        '''
        Process a single iCal entry, adding a new event or updating a current
        one if it is synced to this entry.

        If a synced event does exist, all fields will be overwritten with
        the current values of the iCal entry. The one exception is place.
        The place field will not be overwritten because it would often
        result reintroducing a place_primitive for an Event whose place was
        manually set.
        '''
        try:
            uid = unicode(entry['uid'])
            guid = u'%s;%s' % (self.feed_instance.url, uid)

            # see if we've already processed this record. if so, we're done
            try:
                event = EventMeta.objects.get(key='ical_synced_event', value=guid).event
                new_tracker = None
            except EventMeta.DoesNotExist:
                event = Event()
                new_tracker = EventMeta(key='ical_synced_event', value=guid)

            place_primitive = entry.get('location', '').strip()
            candidate_places = self.feed_instance.candidate_places.all()

            # Location processing -- need a candidate place to get anywhere
            if len(candidate_places) > 0:
                if not place_primitive and len(candidate_places) == 1:
                    # if there's no location specified, and there's one candidate place, safe to assume that's it
                    # TODO: need an explicit go-to primary_place
                    event.place = candidate_places[0]
                elif place_primitive and event.place is None:
                    # TODO: we're super conservative about not overwriting Place here. Introduce field-specific sync meta to do this right.
                    # quick and dirty location parsing (grab all chunks that could be separate entities)

                    # start off with the whole string
                    all_fields = [place_primitive.strip().lower()]
                    # split by commassemicolons, or dashes
                    for delim in (',', ';', '-'):
                        all_fields.append([s.strip().lower() for s in place_primitive.split(delim)])
                    # if parenthesis, grab the inside and outside content
                    p_match = re.match(r'^(.+)\((.+)\)', place_primitive)
                    if p_match:
                        all_fields.append(p_match.group(1).strip().lower())
                        all_fields.append(p_match.group(2).strip().lower())

                    # now, see if any candidate place name or street address is in these fields
                    for candidate in candidate_places:
                        if candidate.name.lower() in all_fields or \
                            candidate.location and candidate.location.address in all_fields:
                            event.place = candidate

            if event.place is None:
                event.place_primitive = place_primitive

            event.name = entry.get('summary', '').strip()
            event.dtstart = process_time(entry['dtstart'], default_tz_str)
            event.dtend = process_time(entry['dtend'], default_tz_str)
            event.description = entry.get('description', '').strip()

            # fitler out evnets before the start filter
            if start_filter is not None and event.dtstart < start_filter:
                    return None

            event.save()

            if self.feed_instance.owner:
                Role.objects.get_or_create(role_type='owner',
                                            organization=self.feed_instance.owner,
                                            event=event)

            if new_tracker:
                new_tracker.event = event
                new_tracker.save()

            return event
        except KeyError:
            # TODO: log message?
            return None
