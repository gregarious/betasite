from haystack import indexes
from onlyinpgh.places.models import Place


class PlaceTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Place
