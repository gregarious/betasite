from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from scenable.specials.models import Special
from scenable.tags.api import TagResource
from scenable.places.api import PlaceResource


### API RESOURCES ###
class SpecialResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    tags = fields.ManyToManyField(TagResource, 'tags', full=True, null=True)

    class Meta:
        queryset = Special.objects.all()
        # allow pass-thru ORM filtering on listed, dtstart, dteend
        filtering = {
            'dstart': ALL,
            'dexpires': ALL,
        }

# Old SpecialData-based Resource
# class SpecialFeedResource(Resource):
#     id = fields.IntegerField('id')
#     title = fields.CharField('title')
#     tags = fields.ManyToManyField(TagResource, 'tags', full=True)
#     place = fields.ForeignKey(PlaceFeedResource, 'place', full=True, null=True)
#     has_coupon = fields.BooleanField('has_coupon', null=True, default=False)

#     class Meta:
#         resource_name = 'special'
#         object_class = SpecialData
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

#     def get_object_list(self, request):
#         specials = Special.objects.all()
#         return [SpecialData(s, request.user) for s in specials]

#     def obj_get_list(self, request=None, **kwargs):
#         specials = Special.objects.filter(**kwargs)
#         user = request.user if request else None
#         return [SpecialData(s, user) for s in specials]

#     def obj_get(self, request=None, **kwargs):
#         special = Special.objects.get(**kwargs)
#         user = request.user if request else None
#         return SpecialData(special, user)
