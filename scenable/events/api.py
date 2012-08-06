from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from haystack.query import SearchQuerySet

from scenable.events.models import Event
from scenable.tags.api import TagResource
from scenable.places.api import PlaceResource


### API RESOURCES ###
class EventResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    tags = fields.ManyToManyField(TagResource, 'tags', full=True, null=True)

    class Meta:
        queryset = Event.objects.all()
        # allow pass-thru ORM filtering on listed, dtstart, dteend
        filtering = {
            'listed': ALL,
            'dtstart': ALL,
            'dtend': ALL,
            # search-query filtering and category filtering is also supported,
            # see build_filters below
        }
        ordering = ['dtend', 'dtstart']

    def build_filters(self, filters=None):
        '''
        Custom filters used for category and searching.
        '''
        if filters is None:
            filters = {}

        orm_filters = super(EventResource, self).build_filters(filters)

        query = filters.get('q')
        category_pk = filters.get('catpk')
        if query is not None:
            sqs = SearchQuerySet().models(Event).load_all().auto_query(query)
            orm_filters["pk__in"] = [i.pk for i in sqs]
        if category_pk is not None:
            orm_filters["tags__pk"] = category_pk

        return orm_filters
