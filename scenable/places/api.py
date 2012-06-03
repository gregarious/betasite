from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from scenable.tags.api import TagResource

from scenable.places.models import Place, Location, HoursListing


### API RESOURCES ###
class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        allowed_methods = ['get']
        excludes = ('id')
        include_resource_uri = False


class PlaceResource(ModelResource):
    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
    tags = fields.ManyToManyField(TagResource, 'tags', full=True, null=True)

    class Meta:
        queryset = Place.objects.all()
        excludes = ('dtcreated', 'parking')
        filtering = {'listed': ALL}     # allow pass-thru ORM filtering on listed

    def dehydrate_hours(self, bundle):
        '''
        Turns a list of HoursListings into raw dicts
        '''
        return [{'hours': listing.hours, 'days': listing.days}
                for listing in bundle.obj.hours]

    def hydrate_hours(self, bundle):
        '''
        Takes raw hours/days dicts and packs them into HoursListings
        '''
        hours = [HoursListing(listing['days'], listing['hours'])
                    for listing in bundle.data['hours']]
        bundle.data['hours'] = hours
        return bundle

    # def obj_get_list(self, request=None, **kwargs):
    #     return super(PlaceResource, self).obj_get_list(request, **kwargs).filter(listed=True)

# class PlaceFeedResource(ModelResource):
#     id = fields.IntegerField('id')
#     name = fields.CharField('name')
#     image = fields.FileField('image')
#     description = fields.CharField('description')
#     tags = fields.ManyToManyField(TagResource, 'tags', full=True)
#     location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
#     is_favorite = fields.BooleanField('is_favorite', null=True, default=False)

#     class Meta:
#         resource_name = 'place'
#         object_class = PlaceData
#         authorization = Authorization()

#     def get_resource_url(self, bundle_or_obj):
#         kwargs = {
#             'resource_name': self._meta.resource_name,
#         }

#         if isinstance(bundle_or_obj, Bundle):
#             kwargs['pk'] = bundle_or_obj.obj.id
#         else:
#             kwargs['pk'] = bundle_or_obj.id

#         if self._meta.api_name is not None:
#             kwargs['api_name'] = self._meta.api_name

#         return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)
