from tastypie.resources import ModelResource
from tastypie import fields
from onlyinpgh.places.models import Place, Location
from onlyinpgh.tags.api import TagResource


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
