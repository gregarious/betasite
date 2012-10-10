from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from haystack.query import SearchQuerySet

from scenable.specials.models import Special
from scenable.places.api import PlaceExtendedStub


### API RESOURCES ###
class SpecialResource(ModelResource):
    place = fields.ForeignKey(PlaceExtendedStub, 'place', full=True, null=True)

    class Meta:
        queryset = Special.objects.all()
        # allow pass-thru ORM filtering on listed, dtstart, dteend
        filtering = {
            'dstart': ALL,
            'dexpires': ALL,
            # search-query filtering and category filtering is also supported,
            # see build_filters below
        }
        ordering = ['dexpires'],
        allowed_methods = ['get']

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
            orm_filters["place__categories__pk"] = category_pk

        return orm_filters

    def dehydrate(self, bundle):
        '''
        If idonly is specified as a flag, the bundle will be reduced to just
        the resource id.
        '''
        if bundle.request.GET.get('idonly', '').lower() == 'true':
            bundle.data = {'id': str(bundle.obj.id)}

        return bundle
