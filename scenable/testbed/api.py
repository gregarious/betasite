from tastypie.resources import ModelResource
from tastypie import fields
from scenable.places.models import Place, Location
from scenable.events.models import Event
from scenable.tags.models import Tag


class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()
        allowed_methods = ['get']
        excludes = ('dtcreated',)
        include_resource_uri = False


class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        allowed_methods = ['get']
        excludes = ('id',)


class PlaceFeedResource(ModelResource):
    class Meta:
        queryset = Place.objects.all()
        allowed_methods = ['get']
        fields = ('name', 'location', 'tags', 'image',)

    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
    tags = fields.ManyToManyField(TagResource, 'tags', full=True)


class PlaceResource(ModelResource):
    class Meta:
        queryset = Place.objects.all()
        allowed_methods = ['get']
        excludes = ('dtcreated',)

        # distance based searching options:
        # 1. Add geo info to database and use something like this http://django-tastypie.readthedocs.org/en/latest/cookbook.html#per-request-alterations-to-the-queryset
        # 2. Do a new endpoint with a non Model-based Resource and handle the get objects call manually
        # 3. Keep old db schema but go through the Tastypie source to see the appropriate place to add the filter (build_filters, deleting from the bundle, etc?)
        #
        # With any choice, might want to create a new endpoint specifically designed to handle the search
        #   ala http://django-tastypie.readthedocs.org/en/latest/cookbook.html#adding-search-functionality
        #   (not a big fan of replicating the whole main behavior of the default Tastypie view,
        #   see if there can be a more surgical approach)

    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
    tags = fields.ManyToManyField(TagResource, 'tags', full=True)

    # def override_urls(self):
    #     return [
    #         url(r"^(?P<resource_name)%s)/distance%s$" % (self._meta.resource_name, trailing_slash()),
    #             self.wrap_view('get_distance_search'), name="place_api-get_distance_search"),
    #     ]

    # def get_distance_search(self, request, **kwargs):
    #     self.method_check(request, allowed=['get'])
    #     self.is_authenticated(request)
    #     self.throttle_check(request)

    #     place_list = super(PlaceResource, self).get_object_list(request).exclude(location=None)
    #     place_list = [p for p in place_list if p.location.is_geocoded()]
    #     lat, lng = request.GET.get('center').split(',')
    #     center_loc = Location(latitude=lat, longitude=lng)
    #     dists = [p.location.distance_from(center_loc) for p in place_list]
    #     return [bundle[1] for bundle in sorted(zip(dists, place_list))]

    # def get_object_list(self, request):
    #     # TODO: error checking on center format, other things. this is fron testbed. reevaluate before putting into production
    #     if request.GET.get('center'):
    #         place_list = super(PlaceResource, self).get_object_list(request).exclude(location=None)
    #         place_list = [p for p in place_list if p.location.is_geocoded()]
    #         lat, lng = request.GET.get('center').split(',')
    #         center_loc = Location(latitude=lat, longitude=lng)
    #         dists = [p.location.distance_from(center_loc) for p in place_list]
    #         return [bundle[1] for bundle in sorted(zip(dists, place_list))]
    #     else:
    #         return super(PlaceResource, self).get_object_list(request)


class EventResource(ModelResource):
    class Meta:
        queryset = Event.objects.all()
        allowed_methods = ['get']
        excludes = ('dtcreated', 'dtmodified',)
    place = fields.ForeignKey(PlaceResource, 'place')
    tags = fields.ToManyField(TagResource, 'tags', full=True)
