from django.test import TestCase
from tastypie.test import ResourceTestCase

from django.db import IntegrityError
from django.utils.encoding import smart_unicode

from scenable.places.models import Place, Location, HoursListing
from scenable.tags.models import Tag
from django.db import transaction

# class LocationModelTest(TestCase):
#     @property
#     def valid_location_base(self):
#         '''
#         property to return a basic Location object that is known to be valid
#         for use in tests
#         '''
#         return Location(country='US',
#                         state='PA',
#                         town='Pittsburgh',
#                         neighborhood=None,
#                         postcode='15213',
#                         address='4620 Henry Street',
#                         latitude=40.446487,
#                         longitude=-79.948524)

#     def test_base_is_valid(self):
#         '''Ensures the location used as the basis of many tests is valid'''
#         self.valid_location_base.save()

#     def test_valid_country_format(self):
#         '''Tests that all country codes have either 0 or 2 characters'''
#         # locations with 1 or >2 letters are no good
#         invalid_countries = ['U', 'USA', 'United States']
#         for invalid_country in invalid_countries:
#             l = self.valid_location_base
#             l.country = invalid_country
#             self.assertRaises(ValidationError, l.save)

#         valid_countries = ['', 'US']
#         for valid_country in valid_countries:
#             l = self.valid_location_base
#             l.country = valid_country
#             l.save()

#     def test_valid_state_format(self):
#         '''Tests that all states have either 0 or 2 characters'''
#         invalid_states = ['P', 'PAX', 'Pennsylvania']
#         for invalid_state in invalid_states:
#             l = self.valid_location_base
#             l.state = invalid_state
#             self.assertRaises(ValidationError, l.save)

#         valid_states = ['', 'PA']
#         for valid_state in valid_states:
#             l = self.valid_location_base
#             l.state = valid_state
#             l.save()

#     def test_geocode_bounds(self):
#         '''
#         Ensures latitude and longitude are within accepted ranges.
#         '''
#         # does an exhaustive 3x3 attempt to set various lat/long values, should only succeed once
#         for lat,lat_valid in ((-90.1,False),(90.1,False),(40.4,True)):
#             for lon,lon_valid in ((-180.1,False),(180.1,False),(-80,True)):
#                 location = Location(latitude=lat,longitude=lon)
#                 if lon_valid and lat_valid:
#                     location.save()    # should be ok
#                 else:
#                     with self.assertRaises(ValidationError):
#                         location.save()

#     def test_complete_geocode(self):
#         '''Ensures any Location with a longitude has a latitude and vice-versa.'''
#         l = self.valid_location_base
#         l.longitude = None
#         self.assertRaises(ValidationError,l.save)
#         l = self.valid_location_base
#         l.latitude = None
#         self.assertRaises(ValidationError,l.save)


class PlaceModelTest(TestCase):
    def test_hours_custom_field(self):
        '''
        Tests cases for custom HoursField. Mostly makes sure everything is
        round-trippable.
        '''
        # create place with no hours or one set to empty list
        Place.objects.create(name='empty', hours=[])
        Place.objects.create(name='implicit_empty')

        # test creation of place with most basic hours content
        firm_hours = [HoursListing('Mon-Fri', '9am - 5pm')]
        Place.objects.create(name='firm', hours=firm_hours)

        # test creation of hours with multiple listings
        bank_hours = [
            HoursListing('Mon-Fri', '9am - 5pm'),
            HoursListing('Sat', '10am - 2pm'),
            HoursListing('Sun', 'Closed')
        ]
        Place.objects.create(name='bank', hours=bank_hours)

        # test creation of hours with commas within hours values
        restaurant_hours = [
            HoursListing('Sun', '11am - 10pm'),
            HoursListing('Mon', 'Closed'),
            HoursListing('Mon-Fri', '11am - 2pm, 4pm - 11pm'),
            HoursListing('Sat', '11am - 10pm')
        ]
        Place.objects.create(name='restaurant', hours=restaurant_hours)

        # assert that hours is non-nullable (empty list means no hours)
        # make a savepoint since we're expecting to trash the transaction
        sid = transaction.savepoint()
        with self.assertRaises(IntegrityError):
            Place.objects.create(name='none', hours=None)
        # IntegrityError must've fired, have to roll back
        transaction.savepoint_rollback(sid)

        # test retrieval of above insertions
        Place.objects.get(name='empty').hours == []
        Place.objects.get(name='implicit_empty').hours == []
        Place.objects.get(name='firm').hours == firm_hours
        Place.objects.get(name='bank').hours == bank_hours
        Place.objects.get(name='restaurant').hours == restaurant_hours


class PlaceResourceTest(ResourceTestCase):
    def setUp(self):
        super(PlaceResourceTest, self).setUp()
        self.detailed_place = Place.objects.create(
            name='detailed',
            description='This is a fun place. So many details!',
            location=Location.objects.create(address='5139 Penn Ave',
                town='Pittsburgh', state='PA', postcode='15224',
                latitude='40.465002', longitude='-79.941352'),
            hours=[HoursListing('Mon-Fri', '9am - 5pm'),
                   HoursListing('Sat', '10pm - 4pm'),
                   HoursListing('Sun', 'Closed')],
            # TODO: add parking
            phone='555-5555',
            url='http://example.com',
            fb_id='1234567890',
            twitter_username='twitter',
            listed=True)
        self.detailed_place.tags.add(Tag.objects.create(name='fun'))
        self.detailed_place.tags.add(Tag.objects.create(name='woo-hoo'))

        self.sparse_listed_place1 = Place.objects.create(
            name='sparse listed 1',
            listed=True)
        self.sparse_listed_place2 = Place.objects.create(
            name='sparse listed 2',
            listed=True)
        self.sparse_unlisted_place = Place.objects.create(
            name='sparse unlisted',
            listed=False)

        self.detail_url = '/api/v1/place/%s' % self.detailed_place.id

    def _test_detailed_equality(self, inst, response_dict):
        '''
        Tests each field of a Place object vs. a PlaceResource dict
        '''
        # these fields can be tested with a simple assertEquals
        simple_equality_keys = ['name', 'phone', 'url', 'fb_id', 'listed',
                                'twitter_username', 'description']
        for k in simple_equality_keys:
            self.assertEquals(getattr(inst, k), response_dict.get(k))

        ### more complex equalities tests
        # test locations
        if inst.location is None:
            self.assertEquals(inst.location, response_dict.get('location'))
        else:
            location_equality_keys = ['address', 'town', 'state', 'postcode']
            for k in location_equality_keys:
                self.assertEquals(getattr(inst.location, k), response_dict['location'].get(k))
            self.assertEquals(smart_unicode(inst.location.latitude), response_dict['location'].get('latitude'))
            self.assertEquals(smart_unicode(inst.location.longitude), response_dict['location'].get('longitude'))

        # test resource uri
        self.assertEquals('/api/v1/place/%s/' % inst.id, response_dict.get('resource_uri'))

        # test hours with special logic
        self.assertEquals(len(inst.hours), len(response_dict.get('hours')))
        for detail_listing, resp_listing in zip(inst.hours, response_dict.get('hours')):
            self.assertEquals(detail_listing.days, resp_listing.get('days'))
            self.assertEquals(detail_listing.hours, resp_listing.get('hours'))

        # ensure all tags are aaccounted for (also check id/name)
        inst_tag_dataset = [{'id': tag.id, 'name': tag.name} for tag in inst.tags.order_by('id')]
        response_dict.get('tags').sort(key=lambda d: d.get('id'))
        self.assertEquals(inst_tag_dataset, response_dict.get('tags'))

    def test_get_list(self):
        '''
        Test basic resource endpoint GET request.
        '''
        resp = self.api_client.get('/api/v1/place/', format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)

        # test expected number of results, and that each id is unique
        self.assertEquals(len(resp['objects']), 4)
        self.assertEquals(len(set([r['id'] for r in resp['objects']])), 4)

        # sanity check for detail item
        detailed_resp = [r for r in resp['objects'] if r['id'] == self.detailed_place.id][0]
        self.assertEquals(self.detailed_place.name, detailed_resp['name'])

    def test_get_listed_only(self):
        '''
        Double check to ensure listed filter is working: important for
        feeds.
        '''
        resp = self.api_client.get('/api/v1/place/?listed=true', format='json')
        self.assertValidJSONResponse(resp)
        resp = self.deserialize(resp)
        self.assertEquals(len(resp['objects']), 3)

    def test_get_detail(self):
        detail_resp = self.api_client.get('/api/v1/place/%s/' % self.detailed_place.id, format='json')
        self.assertValidJSONResponse(detail_resp)
        detail_resp = self.deserialize(detail_resp)
        self._test_detailed_equality(self.detailed_place, detail_resp)

        # ensure the unlisted object can be retrieved directly
        unlisted_resp = self.api_client.get('/api/v1/place/%s/' % self.sparse_unlisted_place.id, format='json')
        self.assertValidJSONResponse(unlisted_resp)
        unlisted_resp = self.deserialize(unlisted_resp)
        self._test_detailed_equality(self.sparse_unlisted_place, unlisted_resp)

# class CloseLocationManagerTest(TestCase):
#     def setUp(self):
#         Location.objects.create(address='5467 Penn Ave', town='Pittsburgh', state='PA',
#                                 postcode='15206', latitude=40.464751, longitude=-79.93344)
#         Location.objects.create(address='5469 Penn Ave', town='Pittsburgh', state='PA',
#                                 postcode='15206', latitude=40.464598, longitude=-79.933881)
#         Location.objects.create(address='5151 Penn Ave', town='Pittsburgh', state='PA',
#                                 postcode='15206', latitude=40.464948, longitude=-79.940899)

#     def test_get_close(self):
#         lat, lng = 40.464237, -79.932940
#         try:
#             Location.close_manager.get_close(address='5467 Penn Ave', latitude=lat, longitude=lng)
#         except Location.DoesNotExist:
#             self.fail('close_get query failed.')

#         # try two tests with the bounds too narrow to find. these should fail to find objects
#         with self.assertRaises(Location.DoesNotExist):
#             Location.close_manager.get_close(address='5467 Penn Ave', latitude=lat, longitude=lng,
#                                         _close_options={'lat_error': 1e-4})
#         with self.assertRaises(Location.DoesNotExist):
#             Location.close_manager.get_close(address='5467 Penn Ave', latitude=lat, longitude=lng,
#                                         _close_options={'lng_error': 1e-4})

#         with self.assertRaises(Location.MultipleObjectsReturned):
#             Location.close_manager.get_close(postcode='15206', latitude=lat, longitude=lng,
#                                         _close_options={'assert_single_match': True})

#     def test_get_close_or_create(self):
#         lat, lng = 40.464237, -79.932940
#         l, created = Location.close_manager.get_close_or_create(address='5467 Penn Ave', latitude=lat, longitude=lng)
#         self.assertFalse(created)
#         l, created = Location.close_manager.get_close_or_create(latitude=lat, longitude=lng)
#         self.assertFalse(created)

#         l, created = Location.close_manager.get_close_or_create(address='5468 Penn Ave', latitude=lat, longitude=lng)
#         self.assertTrue(created)
#         self.assertEquals(l.latitude, lat)
#         self.assertEquals(l.longitude, lng)
