from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from haystack.query import SearchQuerySet

from scenable.common.utils import get_cached_thumbnail

from scenable.tags.api import TagResource
from scenable.places.models import Place, Location, HoursListing
from scenable.events.models import Event
from scenable.specials.models import Special


### API RESOURCES ###
class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        allowed_methods = ['get']
        excludes = ('id')
        include_resource_uri = False


def build_special_stub(special):
    return {
        'title': special.title,
        'expiration_date': special.dexpires
    }


def build_event_stub(event):
    return {
        'name': event.name,
        'dtstart': event.dtstart,
        'dtend': event.dtend,
        'categories': [t for t in event.tags.all()]
    }


class PlaceResource(ModelResource):
    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)
    categories = fields.ManyToManyField(TagResource, 'tags', full=True, null=True)
    # related events and specials are inserted in the dehydrate method

    class Meta:
        queryset = Place.objects.all()
        excludes = ('dtcreated', 'parking')
        filtering = {
            'listed': ALL,  # allow pass-thru ORM filtering on listed
            # search-query filtering and category filtering is also supported,
            # see build_filters below
        }

    def dehydrate(self, bundle):
        '''
        Handles the inclusion of event and special stubs from this place
        '''
        bundle.data['events'] = [build_event_stub(e)
                                for e in Event.objects.filter(place=bundle.obj)
                                                      .order_by('dtend')]
        bundle.data['specials'] = [build_special_stub(s)
                                for s in Special.objects.filter(place=bundle.obj)
                                                        .order_by('dexpires')]
        return bundle

    def dehydrate_image(self, bundle):
        '''
        Ensures data includes a url for an app-sized thumbnail
        '''
        return get_cached_thumbnail(bundle.obj.image, 'app').url \
                if bundle.obj.image \
                else None

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


class PlaceStub(ModelResource):
    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)

    class Meta:
        queryset = Place.objects.all()
        fields = ('name', 'location')


class PlaceExtendedStub(ModelResource):
    location = fields.ForeignKey(LocationResource, 'location', full=True, null=True)

    class Meta:
        queryset = Place.objects.all()
        fields = ('name', 'location', 'id', 'image')

    def dehydrate_image(self, bundle):
        '''
        Ensures data includes a url for an app-sized thumbnail
        '''
        return get_cached_thumbnail(bundle.obj.image, 'app').url \
                if bundle.obj.image \
                else None
