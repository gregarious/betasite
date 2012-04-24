from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from onlyinpgh.places.resources import PlaceFeedResource
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialData
from onlyinpgh.tags.resources import TagResource


### API RESOURCES ###
class SpecialFeedResource(Resource):
    id = fields.IntegerField('id')
    title = fields.CharField('title')
    tags = fields.ManyToManyField(TagResource, 'tags', full=True)
    place = fields.ForeignKey(PlaceFeedResource, 'place', full=True, null=True)
    has_coupon = fields.BooleanField('has_coupon', null=True, default=False)

    class Meta:
        resource_name = 'special'
        object_class = SpecialData
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
        specials = Special.objects.all()
        return [SpecialData(s, request.user) for s in specials]

    def obj_get_list(self, request=None, **kwargs):
        specials = Special.objects.filter(**kwargs)
        user = request.user if request else None
        return [SpecialData(s, user) for s in specials]

    def obj_get(self, request=None, **kwargs):
        special = Special.objects.get(**kwargs)
        user = request.user if request else None
        return SpecialData(special, user)
