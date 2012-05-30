from haystack import indexes
from scenable.specials.models import Special


class SpecialTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    dexpires = indexes.DateTimeField(model_attr='dexpires', null=True)
    dstart = indexes.DateTimeField(model_attr='dstart', null=True)

    def get_model(self):
        return Special
