from tastypie.resources import Resource, ModelResource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from onlyinpgh.places.models import Place, Location
from onlyinpgh.places.viewmodels import PlaceData

from onlyinpgh.tags.resources import TagResource


### API RESOURCES ###
class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        allowed_methods = ['get']
        excludes = ('id',)


class PlaceFeedResource(Resource):
    id = fields.IntegerField('id')
    name = fields.CharField('name')
    image = fields.FileField('image')
    description = fields.CharField('description')
    tags = fields.ManyToManyField(TagResource, 'tags', full=True)
    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
    is_favorite = fields.BooleanField('is_favorite', null=True, default=False)

    class Meta:
        resource_name = 'place'
        object_class = PlaceData
        authorization = Authorization()

    def get_resource_url(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request):
        places = Place.objects.all()
        return [PlaceData(p, request.user) for p in places]

    def obj_get_list(self, request=None, **kwargs):
        places = Place.objects.filter(**kwargs)
        user = request.user if request else None
        return [PlaceData(p, user) for p in places]

    def obj_get(self, request=None, **kwargs):
        place = Place.objects.get(**kwargs)
        user = request.user if request else None
        return PlaceData(place, user)
