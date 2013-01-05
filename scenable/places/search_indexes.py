from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from scenable.places.models import Place


class PlaceTextOnlyIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    listed = indexes.BooleanField(model_attr='listed')

    # FUTURE: Add categories, hours, parking for filtering directly in the SearchQuerySet
    # FUTURE: Add LocationField to enable spatial searching

    # don't bother indexing non-listed objects
    def should_update(self, instance, **kwargs):
        return instance.listed

    def get_model(self):
        return Place

    def get_updated_field(self):
        return 'dtmodified'
