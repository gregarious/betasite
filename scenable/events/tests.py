from django.test import TestCase
from tastypie.test import ResourceTestCase

from scenable.places.models import Place, Location
from scenable.events.models import Event
from scenable.tags.models import Tag

import datetime
from django.utils.timezone import make_naive, get_current_timezone


class EventResourceTest(ResourceTestCase):
    def fakeNow(self):
        return datetime.datetime(2012, 6, 18, 20, 20, tzinfo=get_current_timezone())

    def setUp(self):
        super(EventResourceTest, self).setUp()

        # detailed event, in the future
        self.detailed_event = Event.objects.create(
            name='detailed',
            description='This is a event place. So many details!',
            place=Place.objects.create(
                name='Catapult PGH',
                location=Location.objects.create(address='5139 Penn Ave',
                    town='Pittsburgh', state='PA', postcode='15224',
                    latitude='40.465002', longitude='-79.941352')),
            dtstart=datetime.datetime(2012, 6, 20, 20, 0, tzinfo=get_current_timezone()),
            dtend=datetime.datetime(2012, 6, 20, 22, 30, tzinfo=get_current_timezone()),
            url='http://example.com',
            listed=True)
        self.detailed_event.tags.add(Tag.objects.create(name='fun'))
        self.detailed_event.tags.add(Tag.objects.create(name='cannibals'))

        # event completely in the future
        self.simple_event1 = Event.objects.create(
            name='simple: future',
            dtstart=datetime.datetime(2012, 7, 1, 12, 0, tzinfo=get_current_timezone()),
            dtend=datetime.datetime(2012, 7, 1, 14, 0, tzinfo=get_current_timezone()),
            listed=False)

        # event in progress relative to fakeNow (6/18 @ 20:20)
        self.simple_event2 = Event.objects.create(
            name='simple: in progress',
            dtstart=datetime.datetime(2012, 6, 20, 16, 0, tzinfo=get_current_timezone()),
            dtend=datetime.datetime(2012, 6, 20, 18, 30, tzinfo=get_current_timezone()),
            listed=True)

        # event completely in the past
        self.simple_event3 = Event.objects.create(
            name='simple: past',
            dtstart=datetime.datetime(2012, 6, 3, 20, 0, tzinfo=get_current_timezone()),
            dtend=datetime.datetime(2012, 6, 5, 14, 0, tzinfo=get_current_timezone()),
            listed=True)

        self.detail_url = '/api/v1/event/%s' % self.detailed_event.id

    def _test_datetimes_equality(self, inst, response_dict):
        '''
        Ensures dtstart/dtend objects stored in inst match the serialized
        versions in response_dict.

        NOTE: Tastypie's out-of-the-box behavior returns naive ISO-
              formatted datetimes relative to settings.DATE_TIME. Thus, we
              have to convert our instance's datetimes first.
        '''
        iso_dtstart = make_naive(inst.dtstart, get_current_timezone()).isoformat()
        iso_dtend = make_naive(inst.dtend, get_current_timezone()).isoformat()
        self.assertEquals(iso_dtstart, response_dict.get('dtstart'))
        self.assertEquals(iso_dtend, response_dict.get('dtend'))

    def _test_detailed_equality(self, inst, response_dict):
        '''
        Tests each field of a Place object vs. a PlaceResource dict
        '''
        # these fields can be tested with a simple assertEquals
        simple_equality_keys = ['name', 'description', 'url', 'allday',
                                'place_primitive', 'listed']
        for k in simple_equality_keys:
            self.assertEquals(getattr(inst, k), response_dict.get(k))

        ### more complex equalities tests
        # test times
        self._test_datetimes_equality(inst, response_dict)

        # test place api url
        if inst.place is None:
            self.assertEquals(inst.place, response_dict.get('place'))
        else:
            self.assertEquals('/api/v1/place/%s/' % inst.id, response_dict.get('place'))

        # test resource uri
        self.assertEquals('/api/v1/event/%s/' % inst.id, response_dict.get('resource_uri'))

        # ensure all tags are aaccounted for (also check id/name)
        inst_tag_dataset = [{'id': tag.id, 'name': tag.name} for tag in inst.tags.order_by('id')]
        response_dict.get('tags').sort(key=lambda d: d.get('id'))
        self.assertEquals(inst_tag_dataset, response_dict.get('tags'))

    def test_get_list(self):
        '''
        Test basic resource endpoint GET request.
        '''
        resp = self.api_client.get('/api/v1/event/', format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)

        # test expected number of results, and that each id is unique
        self.assertEquals(len(resp['objects']), 4)
        self.assertEquals(len(set([r['id'] for r in resp['objects']])), 4)

        # sanity check for detail item
        detailed_resp = [r for r in resp['objects'] if r['id'] == self.detailed_event.id][0]
        self.assertEquals(self.detailed_event.name, detailed_resp['name'])

    def test_get_listed_only(self):
        '''
        Double check to ensure listed filter is working: important for
        feeds.
        '''
        resp = self.api_client.get('/api/v1/event/?listed=true', format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)
        self.assertEquals(len(resp['objects']), 3)

    def test_get_incomplete_listed_only(self):
        '''
        Double check to ensure listed and dtend filter is working for list
        results: this is a very likely scenario.
        '''
        resp = self.api_client.get('/api/v1/event/?listed=true&dtend__gte=%s' % self.fakeNow().isoformat(), format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)
        resp_names = set([r['name'] for r in resp['objects']])
        self.assertEquals(set(['simple: in progress', 'detailed']), resp_names)

    def test_get_detail(self):
        detail_resp = self.api_client.get('/api/v1/event/%s/' % self.detailed_event.id, format='json')
        self.assertValidJSONResponse(detail_resp)
        detail_resp = self.deserialize(detail_resp)
        self._test_detailed_equality(self.detailed_event, detail_resp)

        # ensure the unlisted object can be retrieved directly
        unlisted_resp = self.api_client.get('/api/v1/event/%s/' % self.simple_event1.id, format='json')
        self.assertValidJSONResponse(unlisted_resp)
        unlisted_resp = self.deserialize(unlisted_resp)
        self._test_detailed_equality(self.simple_event1, unlisted_resp)
