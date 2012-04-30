from haystack import indexes
from onlyinpgh.specials.models import Special


class SpecialTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Special
