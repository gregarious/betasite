from haystack import indexes
from scenable.places.models import Place


# TODO: Need to ensure 500 errors aren't thrown when indexer chokes on model save
class PlaceTextOnlyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    listed = indexes.BooleanField(model_attr='listed')
    # TODO: add hours and parking for filtering by those

    def should_update(self, instance, **kwargs):
        return instance.listed

    def get_model(self):
        return Place
