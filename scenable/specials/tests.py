from django.test import TestCase
from tastypie.test import ResourceTestCase

from scenable.places.models import Place
from scenable.specials.models import Special
from scenable.tags.models import Tag

import datetime


class SpecialResourceTest(ResourceTestCase):
    def fakeToday(self):
        return datetime.date(2012, 6, 18)

    def setUp(self):
        super(SpecialResourceTest, self).setUp()

        # create some dummy places so FK relationship isn't just place.id=1
        for i in range(10):
            Place.objects.create(name='dummy%s' % i)

        # detailed special, in the future
        self.detailed_special = Special.objects.create(
            title='detailed',
            description='This is a special special. La la la.',
            points=100,
            total_sold=23,
            total_available=77,
            place=Place.objects.create(name='Catapult PGH'),
            dstart=datetime.date(2012, 6, 1),
            dexpires=datetime.date(2012, 6, 30))
        self.detailed_special.tags.add(Tag.objects.create(name='fun'))
        self.detailed_special.tags.add(Tag.objects.create(name='zebra-skin'))

        # special completely in the future
        self.simple_special1 = Special.objects.create(
            title='simple: future',
            place=Place.objects.create(name='dummy'),
            dstart=datetime.date(2012, 7, 1),
            dexpires=datetime.date(2012, 7, 31))

        # special in progress relative to fakeNow (6/18 @ 20:20)
        self.simple_special2 = Special.objects.create(
            title='simple: in progress',
            place=Place.objects.create(name='dummy2'),
            dstart=datetime.date(2012, 6, 1),
            dexpires=datetime.date(2012, 12, 31))

        # special completely in the past
        self.simple_special3 = Special.objects.create(
            title='simple: past',
            place=Place.objects.create(name='dummy3'),
            dstart=datetime.date(2012, 5, 18),
            dexpires=datetime.date(2012, 5, 24))

        self.detail_url = '/api/v1/special/%s' % self.detailed_special.id

    def _test_dates_equality(self, inst, response_dict):
        '''
        Ensures dstart/dexpires objects stored in inst match the serialized
        versions in response_dict.
        '''
        if inst.dstart is None:
            self.assertEquals(None, response_dict.get('dstart'))
        else:
            self.assertEquals(inst.dstart.isoformat(), response_dict.get('dstart'))
        if inst.dexpires is None:
            self.assertEquals(None, response_dict.get('dexpires'))
        else:
            self.assertEquals(inst.dexpires.isoformat(), response_dict.get('dexpires'))

    def _test_detailed_equality(self, inst, response_dict):
        '''
        Tests each field of a Place object vs. a PlaceResource dict
        '''
        # these fields can be tested with a simple assertEquals
        simple_equality_keys = ['title', 'description', 'points',
                                'total_available', 'total_sold']
        for k in simple_equality_keys:
            self.assertEquals(getattr(inst, k), response_dict.get(k))

        ### more complex equalities tests
        # test times
        self._test_dates_equality(inst, response_dict)

        # test place api url
        if inst.place is None:
            self.assertEquals(inst.place, response_dict.get('place'))
        else:
            self.assertEquals('/api/v1/place/%s/' % inst.place.id, response_dict.get('place'))

        # test resource uri
        self.assertEquals('/api/v1/special/%s/' % inst.id, response_dict.get('resource_uri'))

        # ensure all tags are aaccounted for (also check id/name)
        inst_tag_dataset = [{'id': tag.id, 'name': tag.name} for tag in inst.tags.order_by('id')]
        response_dict.get('tags').sort(key=lambda d: d.get('id'))
        self.assertEquals(inst_tag_dataset, response_dict.get('tags'))

    def test_get_list(self):
        '''
        Test basic resource endpoint GET request.
        '''
        resp = self.api_client.get('/api/v1/special/', format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)

        # test expected number of results, and that each id is unique
        self.assertEquals(len(resp['objects']), 4)
        self.assertEquals(len(set([r['id'] for r in resp['objects']])), 4)

        # sanity check for detail item
        detailed_resp = [r for r in resp['objects'] if r['id'] == self.detailed_special.id][0]
        self.assertEquals(self.detailed_special.title, detailed_resp['title'])

    def test_get_list_filters(self):
        '''
        Double check to ensure dstart/dexpires filters are working.
        '''
        isotoday = self.fakeToday().isoformat()
        resp = self.api_client.get('/api/v1/special/?dexpires__gte=%s&dstart__lte=%s' % (isotoday, isotoday), format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)
        resp_titles = set([r['title'] for r in resp['objects']])
        self.assertEquals(set(['simple: in progress', 'detailed']), resp_titles)

    def test_get_detail(self):
        detail_resp = self.api_client.get('/api/v1/special/%s/' % self.detailed_special.id, format='json')
        self.assertValidJSONResponse(detail_resp)
        detail_resp = self.deserialize(detail_resp)
        self._test_detailed_equality(self.detailed_special, detail_resp)

        # ensure the unlisted object can be retrieved directly
        unlisted_resp = self.api_client.get('/api/v1/special/%s/' % self.simple_special1.id, format='json')
        self.assertValidJSONResponse(unlisted_resp)
        unlisted_resp = self.deserialize(unlisted_resp)
        self._test_detailed_equality(self.simple_special1, unlisted_resp)
