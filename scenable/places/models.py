from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError

from south.modelsinspector import add_introspection_rules

from scenable.tags.models import Tag
from scenable.common.core.viewmodels import ViewModel
from scenable.common.utils import CSVPickler

from django.contrib.auth.models import User
from scenable.common.utils import precache_thumbnails

import math
import urllib


class CloseLocationManager(models.Manager):
    def get_close(self, **kwargs):
        '''
        Runs a get query that allows some leeway on exact matching of
        the geocoding data. Assuming any results are close (within some
        error tolerance), the closest one to the input will be returned.

        In addition to normal arguments, a dict of options with the
        keyword name '_close_options' can be passed in with the following
        keys:
        - lat_error (+/- bounds put on latitude [default: .001])
        - lng_error (+/- bounds put on longitude [default: .001])
        - assert_single_match (raise an error if more than one result
            matches the full query with bounding criteria [default: False])
        '''
        assert kwargs, 'get_close() only support keyword arguments'

        close_options = kwargs.pop('_close_options', {})
        lat_error = close_options.get('lat_error', 1e-3)
        lng_error = close_options.get('lng_error', 1e-3)
        assert_single_match = close_options.get('assert_single_match', False)

        # remove the equality constraints and add a pair of bounding ones
        lat = kwargs.get('latitude')
        if lat is not None:
            kwargs.pop('latitude')
            kwargs['latitude__lt'] = lat + lat_error
            kwargs['latitude__gt'] = lat - lat_error
        lng = kwargs.get('longitude')
        if lng is not None:
            kwargs['longitude__lt'] = lng + lng_error
            kwargs['longitude__gt'] = lng - lng_error

        # if we can only have one match (or no geocoding in query anyway), just run regular get
        if assert_single_match or (lng is None and lat is None):
            return self.get(**kwargs)

        # otherwise, we need to run filter with the relaxed constraints and then find the closest result among them
        results = self.filter(**kwargs)
        if len(results) == 0:
            raise Location.DoesNotExist("Location matching 'close query' does not exist")
        elif len(results) == 1:
            return results[0]
        else:
            calc_distance = lambda p0, p1: math.sqrt(math.pow(float(p1[0]) - float(p0[0]), 2) +
                                                     math.pow(float(p1[1]) - float(p0[1]), 2))
            if lat is None:
                lat = 0
            if lng is None:
                lng = 0
            anchor = (lat, lng)
            best, best_dist = None, float('inf')
            for r in results:
                point = (r.latitude or 0, r.longitude or 0)
                dist = calc_distance(anchor, point)
                if dist < best_dist:
                    best, best_dist = r, dist
            return best

    def get_close_or_create(self, **kwargs):
        '''
        Runs get_or_create query with some leeway on matching geocoding
        criteria for the get attempt.

        Note: be careful on using this function with address-less
        locations that just feature geocoding. Doing so will encourage all
        address-less locations to converge to focus points (the first
        one created).

        Accepts same _close_options as get_close() -- see that method's
        docstring for more details.

        Note, this involves one extra query than a normal get_or_create
        when the get_close fails because I didn't want to muck around
        in duplicating the intricaies of Django's own get_or_create.
        '''
        try:
            return self.get_close(**kwargs), False
        except Location.DoesNotExist:
            kwargs.pop('_close_options', {})
            return self.get_or_create(**kwargs)


class Location(models.Model, ViewModel):
    '''
    Handles specific information about where a physical place is located. Should
    rarely be exposed without a Place wrapping it on the front end.
    '''
    class Meta:
        ordering = ['address', 'latitude']

    # TODO: probably take out defaults for town and state, definitely country
    # 2-char country code (see http://en.wikipedia.org/wiki/ISO_3166-1)
    country = models.CharField(max_length=2, blank=True,
                                validators=[MinLengthValidator(2)],
                                default='US')

    # should only include 2-letter codes (US states and CA provinces obey this)
    state = models.CharField(max_length=2, blank=True,
                                validators=[MinLengthValidator(2)])

    town = models.CharField(max_length=60, blank=True)

    postcode = models.CharField(max_length=10, blank=True)
    address = models.TextField('street address (or premise)', blank=True)

    # should always be between -90,90
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True,
                                    validators=[MinValueValidator(-90),
                                                MaxValueValidator(90)])
    # should always be between -180,180
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    blank=True, null=True,
                                    validators=[MinValueValidator(-180),
                                                MaxValueValidator(180)])

    objects = models.Manager()
    close_manager = CloseLocationManager()

    def save(self, *args, **kwargs):
        self.full_clean()        # run field validators
        # ensure country and state are saved in db in uppercase
        if self.country:
            self.country = self.country.upper()
        if self.state:
            self.state = self.state.upper()
        return super(Location, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        # ensure latitude and longitude exist in pairs
        if self.latitude is not None and self.longitude is None or \
            self.longitude is not None and self.latitude is None:
            raise ValidationError('If geocoding information is available, buth longitude and latitude must be specified')
        return super(Location, self).clean(*args, **kwargs)

    def __unicode__(self):
        if self.address:
            return self.address if self.address else u''
        elif self.latitude or self.longitude:
            lat_s = u'%.3f' % self.latitude if self.latitude is not None else u'-'
            lon_s = u'%.3f' % self.longitude if self.longitude is not None else u'-'
            return u'<No address: Coords: (%s,%s)>' % (lat_s, lon_s)
        return u''

    @property
    def full_string(self):
        s = ''
        if self.address:
            s += '%s, ' % self.address
        if self.town:
            s += '%s, ' % self.town

        if self.state and self.postcode:
            s += '%s %s, ' % (self.state, self.postcode)
        elif self.state:
            s += '%s, ' % self.state
        elif self.postcode:
            s += '%s, ' % self.postcode

        if self.latitude or self.longitude:
            s += '(%s,%s)' % ('%.3f' % self.latitude if self.latitude else '-',
                              '%.3f' % self.longitude if self.latitude else '-')

        return s.rstrip(', ')

    def is_geocoded(self):
        return self.latitude is not None and self.longitude is not None

    def distance_from(self, other_location, fast=False):
        '''
        Returns distance in km between two geolocated places.

        Normally operates assuming a spherical projection of the earth,
        but can be more efficient by assuming an equarectangular
        projection (http://www.movable-type.co.uk/scripts/latlong.html).
        Enable this behavior by specifying fast=True.

        Returns None if self or other_location has incomplete geocoding.
        '''
        R = 6371     # mean earth radius in km
        if not self.is_geocoded() or not other_location.is_geocoded():
            return None

        to_rad = lambda x: 0.01745327 * float(x)
        lat1, lat2 = to_rad(self.latitude), to_rad(other_location.latitude)
        lng1, lng2 = to_rad(self.longitude), to_rad(other_location.longitude)
        if fast:
            x = (lng2 - lng1) * math.cos((lat1 + lat2) / 2)
            y = (lat2 - lat1)
            return R * math.sqrt(pow(x, 2) + pow(y, 2))
        else:
            try:
                return R * math.acos(math.sin(lat1) * math.sin(lat2) +
                                      math.cos(lat1) * math.cos(lat2) *
                                      math.cos(lng2 - lng1))
            except:     # kind of a cop-out, but this should actually mean 0 distance if inputs are sane
                return 0

    def directions_link(self):
        daddr = ''
        if self.address:
            daddr = self.address
            if self.postcode:
                daddr += ', ' + self.postcode
        elif self.is_geocoded:
            daddr = '(%f,%f)' % (float(self.longitude), float(self.latitude))

        if not daddr:
            return None
        else:
            return 'http://maps.google.com/maps?' + urllib.urlencode({'daddr': daddr})


class ListedPlaceManager(models.Manager):
    def get_query_set(self):
        return super(ListedPlaceManager, self).get_query_set().filter(listed=True)


# TODO: Note problem with HoursListings in admin interface. Interface will
#  call to_python when pulling from db, and display this data as-is
#  (e.g. "[]" or "[<scenable.places.models.HoursListing object at 0x10ecfebd0>, ...]")
#  didn't look into how to fix this
class HoursListing(object):
    def __init__(self, days, hours):
        self.days = days
        self.hours = hours

    def __unicode__(self):
        return u'<HoursListing: "%s: %s">' % (self.days, self.hours)

    def __eq__(self, other):
        return self.days == other.days and self.hours == other.hours


class HoursField(models.TextField):
    description = "List of HoursListings"
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.pickler = CSVPickler()
        super(HoursField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(HoursField, self).to_python(value)
        if isinstance(value, list) or value is None:
            return value
        return [HoursListing(*pair) for pair in self.pickler.from_csv(value)]

    def get_prep_value(self, value):
        if value is None:
            prepped = value
        else:
            tuples = [(v.days.strip(), v.hours.strip()) for v in value]
            prepped = self.pickler.to_csv(tuples)
        return super(HoursField, self).get_prep_value(prepped)

    # TODO: do a custom widget/field for this
    def formfield(self, **kwargs):
        return super(HoursField, self).formfield(**kwargs)


# need to register custom field with South
add_introspection_rules([], ["^scenable\.places\.models\.HoursField"])


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'categories'

    label = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return self.label


class Place(models.Model, ViewModel):
    '''
    Handles information about places.
    '''
    class Meta:
        ordering = ['name']

    dtcreated = models.DateTimeField('dt created', auto_now_add=True)
    name = models.CharField(max_length=200, blank=True)
    location = models.ForeignKey(Location, blank=True, null=True)

    image = models.ImageField(upload_to='img/p', null=True, blank=True)
    description = models.TextField(blank=True)

    # place-specific categories. more specific than tags.
    categories = models.ManyToManyField(Category, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)

    hours = HoursField('List of HoursListing', blank=True)
    parking = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)

    url = models.URLField(blank=True)
    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    listed = models.BooleanField('place publicly listed on site?', default=True)

    objects = models.Manager()
    listed_objects = ListedPlaceManager()

    def __unicode__(self):
        s = self.name
        if self.location and self.location.address:
            s += u' (%s)' % self.location.address
        return s

    def save(self, *args, **kwargs):
        super(Place, self).save(*args, **kwargs)
        if self.image:
            # pre-cache common sized thumbnails
            try:
                precache_thumbnails(self.image)
            # never let these lines interrupt anything
            except Exception as e:
                print 'error caching thumbnails', e
                # TODO: log error

    def to_data(self, *args, **kwargs):
        '''
        Manually handle location and tag entries.
        '''
        data = super(Place, self).to_data(*args, **kwargs)
        data.pop('location_id')
        if self.location:
            data['location'] = self.location.to_data(*args, **kwargs)
        data['tags'] = [t.to_data(*args, **kwargs) for t in self.tags.all()]
        return data

    @models.permalink
    def get_absolute_url(self):
        return ('place-detail', (), {'pid': self.id})

    def mark_favorite(self, user):
        '''
        Adds Favorite object to this Place's favorite_set.

        Returns True if new favorite created, False if already existed
        '''
        _, created = self.favorite_set.get_or_create(user=user)
        return created

    def unmark_favorite(self, user):
        '''
        Deletes Favorite object from this Place's favorite_set.

        Returns True if favorite existed, False if it already didn't.
        '''
        favs = self.favorite_set.filter(user=user)
        fav_exists = favs.count() != 0
        favs.delete()
        return fav_exists

    def parking_unpacked(self):
        return self.parking_as_obj().to_data()

    def parking_as_obj(self):
        return Parking.deserialize(self.parking)

    def set_parking(self, parking):
        self.parking = parking.serialize()


class PlaceMeta(models.Model):
    '''
    Handles meta information for a Place.

    Current possible keys & values:
    - fb_synced_field: value is name of Place field retrieved from FB
    - fb_last_synced: value is UTC time (in ISO format) fields last synced
        with FB
    '''
    place = models.ForeignKey(Place)
    key = models.CharField(max_length=32)
    value = models.TextField()

    def __unicode__(self):
        val = self.value if len(self.value) < 20 \
                else self.value[:16] + '...'
        return u'%s: %s' % (self.key, val)


class Favorite(models.Model):
    user = models.ForeignKey(User)
    place = models.ForeignKey(Place)
    dtcreated = models.DateTimeField('Time user first added as favorite', auto_now_add=True)

    def __unicode__(self):
        return unicode(self.user) + u'@' + unicode(self.place)


class Parking(ViewModel):
    '''
    Object to handle parking options.
    '''
    choices = (('street', 'Street'),
               ('lot', 'Lot'),
               ('garage', 'Garage'),
               ('valet', 'Valet'))

    def __init__(self):
        self.parking_options = []
        self.pickler = CSVPickler()

    def add_option(self, option):
        if option not in [c[0] for c in Parking.choices]:
            raise ValueError('Invalid parking option')
        self.parking_options.append(option)

    def to_data(self):
        choice_map = dict(Parking.choices)
        return [choice_map[option_key] for option_key in self.parking_options]

    @classmethod
    def deserialize(cls, data):
        inst = Parking()
        inst.parking_options = [row[0] for row in inst.pickler.from_csv(data)]
        return inst

    def serialize(self):
        return self.pickler.to_csv([[opt] for opt in self.parking_options])

    def __str__(self):
        return self.serialize()
