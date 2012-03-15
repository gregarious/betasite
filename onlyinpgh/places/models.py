from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError

from onlyinpgh.tags.models import Tag
from onlyinpgh.common.core.viewmodels import ViewModel

from math import sqrt, pow


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
            calc_distance = lambda p0, p1: sqrt(pow(float(p1[0]) - float(p0[0]), 2) +
                                                pow(float(p1[1]) - float(p0[1]), 2))
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


class Place(models.Model, ViewModel):
    '''
    Handles information about places.
    '''
    class Meta:
        ordering = ['name']

    dtcreated = models.DateTimeField('dt created', auto_now_add=True)
    name = models.CharField(max_length=200, blank=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    image_url = models.URLField(max_length=400)
    tags = models.ManyToManyField(Tag, blank=True)

    def __unicode__(self):
        s = self.name
        if self.location and self.location.address:
            s += u' (%s)' % self.location.address
        return s

    def to_data(self):
        '''
        Overrides ViewModel's to_data to ignore dtcreated and
        extract tags.
        '''
        # TODO: remove temporary placeholder
        image_url = self.image_url or 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

        return {
            'id': self.id,
            'name': self.name,
            'location': self.location.to_data(),
            'image_url': image_url,
            'tags': [tag.to_data() for tag in self.tags.all()]
        }


class PlaceProfile(models.Model, ViewModel):
    '''
    Extended information about a place
    '''
    class Meta:
        ordering = ['place']

    place = models.OneToOneField(Place)
    description = models.TextField(blank=True)
    hours = models.TextField('comma-separated Day:Hour entries', blank=True)
    parking = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)

    url = models.URLField(blank=True)
    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    def __unicode__(self):
        return unicode(self.place)


class PlaceMeta(models.Model):
    '''
    Handles meta information for a Place.
    '''
    place = models.ForeignKey(Place)
    key = models.CharField(max_length=32)
    value = models.TextField()

    def __unicode__(self):
        val = self.value if len(self.value) < 20 \
                else self.value[:16] + '...'
        return u'%s: %s' % (self.key, val)
