from haystack import indexes
from scenable.places.models import Place


class PlaceTextOnlyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    listed = indexes.BooleanField(model_attr='listed')

    # FUTURE: Add categories, hours, parking for filtering directly in the SearchQuerySet
    # FUTURE: Add LocationField to enable spatial searching

    # don't bother indexing non-listed objects
    def should_update(self, instance, **kwargs):
        return instance.listed

    def get_model(self):
        return Place
