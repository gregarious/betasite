from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from haystack.query import SearchQuerySet

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
        filtering = {
            'listed': ALL,  # allow pass-thru ORM filtering on listed
            # search-query filtering and category filtering is also supported,
            # see build_filters below
        }

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

    def build_filters(self, filters=None):
        '''
        Custom filters used for category and searching.
        '''
        if filters is None:
            filters = {}

        orm_filters = super(PlaceResource, self).build_filters(filters)

        query = filters.get('q')
        category_pk = filters.get('catpk')
        if query is not None:
            sqs = SearchQuerySet().models(Place).load_all().auto_query(query)
            orm_filters["pk__in"] = [i.pk for i in sqs]
        if category_pk is not None:
            orm_filters["tags__pk"] = category_pk

        return orm_filters
