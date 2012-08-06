from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from haystack.query import SearchQuerySet

from scenable.places.models import Place
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
            # search-query filtering and category filtering is also supported,
            # see build_filters below
        }
        ordering = ['dexpires']

    def build_filters(self, filters=None):
        '''
        Custom filters used for category and searching.
        '''
        if filters is None:
            filters = {}

        orm_filters = super(SpecialResource, self).build_filters(filters)

        query = filters.get('q')
        category_pk = filters.get('catpk')
        if query is not None:
            sqs = SearchQuerySet().models(Special).load_all().auto_query(query)
            orm_filters["pk__in"] = [i.pk for i in sqs]

        # category actually operates on Place and Special
        if category_pk is not None:
            orm_filters["place__tags__pk"] = category_pk

        return orm_filters
