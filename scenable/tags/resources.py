from tastypie.resources import ModelResource
from scenable.tags.models import Tag


class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()
        allowed_methods = ['get']
        excludes = ('dtcreated',)
        include_resource_uri = False
